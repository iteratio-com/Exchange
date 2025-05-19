#!/usr/bin/env python3

from ast import literal_eval
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import cmk.gui.forms as forms
import cmk.gui.pages
import cmk.gui.sites as sites
import cmk.gui.userdb as userdb
import cmk.utils.paths as cmk_paths
import paramiko
from cmk.gui.breadcrumb import Breadcrumb, make_simple_page_breadcrumb
from cmk.gui.htmllib.header import make_header
from cmk.gui.htmllib.html import html
from cmk.gui.http import request
from cmk.gui.i18n import _
from cmk.gui.logged_in import user
from cmk.gui.main_menu import mega_menu_registry
from cmk.gui.page_menu import (
    PageMenu,
    PageMenuDropdown,
    PageMenuEntry,
    PageMenuTopic,
    make_simple_link,
)
from cmk.gui.table import init_rowselect, table_element
from cmk.gui.utils.flashed_messages import flash, get_flashed_messages
from cmk.gui.utils.transaction_manager import transactions
from cmk.gui.utils.urls import make_confirm_delete_link, makeactionuri
from cmk.gui.weblib import selection_id
from livestatus import SiteId


CONFIG_FILENAME = "/sms-notifications.conf"
CONFIG_FILE_STR = cmk_paths.var_dir + CONFIG_FILENAME
CONFIG_FILE = Path(CONFIG_FILE_STR)
SERVICE_NAME_FOR_TEST_NOTIFICATION = "Test Notification"

from cmk.gui.watolib.sites import SiteManagement

###### Documentation
# Prerequisites:
# * A host, with the name of the contact group
# * The host has no datasource, no IP address
# * The contact group must be actively assigned to the host (on the host, not by rule)
# * There is a Nagios rule for the host(s) with the following properties:
#    - Service description = "Test Notification"
#    - Command line = echo "Please execute 'Fake Check Results' to trigger a notification"; exit 0
#    - no freshness check
# * SCP is used to distribute the config file in distributed monitoring, for which the site users must be able to log in to the Checkmk sites without a password.
# OMD[kplus]:~$ ssh-keygen
# OMD[kplus]:~$ ssh-copy-id -i ~/.ssh/id_rsa.pub slave_kplus@192.168.178.104


def get_usable_contact_groups() -> dict[str, str]:
    usable = []
    for user, data in userdb.load_users().items():
        if data.get("pager"):
            for group_title in data.get("contactgroups", []):
                if group_title not in usable:
                    usable.append(group_title)
    sites.live().set_prepend_site(True)
    only_contact = []
    usable_dict = {}
    for site, contact_group_title, user, contact in sites.live().query("GET contactgroups\n"):
        if contact == "name" or contact == "all" or contact in only_contact:
            continue
        for i in usable:
            if i == contact:
                usable_dict[contact] = contact_group_title
        only_contact.append(contact)
    return usable_dict


def inital_read():
    if CONFIG_FILE.is_file():
        with open(CONFIG_FILE, "r") as f:
            notification_config = f.read()
    else:
        notification_config = "{}"
    config_dict = literal_eval(notification_config)
    contact_groups_title = {}
    usable_contact_groups = get_usable_contact_groups()
    sites.live().set_prepend_site(True)
    for site, contact_group_title, user, contact in sites.live().query("GET contactgroups\n"):
        if contact == "name" or contact == "all":
            continue
        if not usable_contact_groups.get(contact):
            continue
        contact_groups_title[contact] = contact_group_title
        config_dict.setdefault(contact, {})
        for u in user:
            if config_dict[contact].get(u) == None:
                config_dict[contact][u] = 0
    return (config_dict, contact_groups_title)


def write_config(data: dict[str, Any]):
    with open(CONFIG_FILE, "w") as f:
        f.write(str(data))


def sms_table() -> None:
    config_dict, contact_groups_title = inital_read()

    for group_title, werks in config_dict.items():
        with table_element(
            title=contact_groups_title.get(group_title),
            limit=None,
            searchable=True,
            sortable=True,
            css="werks",
            omit_if_empty=True,
        ) as table:
            usable = []
            for user, data in userdb.load_users().items():
                if group_title in data.get("contactgroups", []):
                    if data.get("pager"):
                        usable.append(
                            (
                                group_title,
                                config_dict[group_title].get(user, 0),
                                user,
                                data.get("alias"),
                                data.get("pager"),
                            )
                        )
            for user in usable:
                table.row()
                table.cell(
                    html.checkbox(
                        varname=f"_cb_{user[0]}--{user[2]}",
                        id_=f"_cb_{user[0]}--{user[2]}",
                    ),
                    css=["checkbox"],
                )
                table.cell(_("User"), user[2], css=["number narrow"])
                table.cell(_("User Alias"), user[3], css=["number narrow"])
                table.cell(_("Pager Number"), user[4], css=["number narrow"])


def handle_acknowledgement():
    if not transactions.check_transaction():
        return

    if request.var("_send_sms"):
        # now it will send a sms to contact group name
        contact = request.var("_send_sms")

        sites.live().set_prepend_site(True)
        infos = sites.live().query(
            query=f"GET services\nColumns: description state host_contact_groups\nFilter: host_name = {contact}\n"
        )
        srv_name = SERVICE_NAME_FOR_TEST_NOTIFICATION
        if not infos or not infos[0]:
            flash(
                f"There is no Host '{contact}' with Service '{srv_name}' (Nothing Send!)",
                msg_type="error",
            )
            html.reload_whole_page()

        if len(infos) != 1:
            flash(
                f"There are multiple Host(s) for '{contact}' or multiple Service(s) '{srv_name}' (Nothing Send!)",
                msg_type="error",
            )
            html.reload_whole_page()
            return

        checkmk_site, srv_searched, srv_state, host_contact_groups = infos[0]
        try:
            host_contact_groups.remove("all")
        except:
            pass

        if srv_searched != srv_name:
            flash(
                f"Host '{contact}' has no Service '{srv_name}' (Nothing Send!)",
                msg_type="error",
            )
            html.reload_whole_page()
            return

        if srv_state != 0:
            flash(
                f"Service of Host '{contact}' and Service '{srv_name}' is already triggered, please try after next check interval (Nothing Send!)",
                msg_type="error",
            )
            html.reload_whole_page()
            return

        if srv_state != 0:
            flash(
                f"Service of Host '{contact}' and Service '{srv_name}' is already triggered, please try after next check interval (Nothing Send!)",
                msg_type="error",
            )
            html.reload_whole_page()
            return

        if contact not in host_contact_groups:
            flash(
                f"Host '{contact}' is not in Contact Group '{contact}' (Nothing Send!)",
                msg_type="error",
            )
            html.reload_whole_page()
            return

        cmd = (
            f"PROCESS_SERVICE_CHECK_RESULT;{contact};{srv_name};2;Test Notification from SMS Config"
        )
        sites.live().command(cmd, SiteId(checkmk_site))
        flash(
            f"A Messages to Contact group <b>{contact}</b> has been send.",
            msg_type="message",
        )

        # FIXME: This is not good
        # cmd = f"COMMAND [{int(time())}] PROCESS_SERVICE_CHECK_RESULT;{contact};{srv_name};2;Test Notification from SMS Config"
        # full_cmd = f"""{os.getenv('OMD_ROOT')}/bin/lq "{cmd}" """
        # os.system(full_cmd)
        html.reload_whole_page()

    elif request.var("_safe_config"):
        selection: list[str] = user.get_rowselection(selection_id(), "carrier")
        config_dict, contact_groups_title = inital_read()
        need_user_cg = list(contact_groups_title)

        for cg, user_dict in config_dict.items():
            for u in user_dict:
                config_dict[cg][u] = 0

        for select in selection:
            s = select[4:]
            cg = s.split("--")[0]
            u = "--".join(s.split("--")[1:])
            config_dict[cg][u] = 1
            try:
                need_user_cg.remove(cg)
            except ValueError:
                pass

        if need_user_cg:
            txt = f"""<b>Error:</b> Missing User for flowing Group(s): <b>{', '.join(need_user_cg)}</b><br>"""
            flash(txt, msg_type="error")
            html.reload_whole_page()
        else:
            write_config(data=config_dict)
            flash("Successful Write Config (local)", msg_type="message")
            external_sites = {}
            master_site = ""
            for site, site_infos in SiteManagement.load_sites().items():
                socket = site_infos.get("socket", [])
                if socket[0] == "tcp":
                    external_sites[site] = socket[1].get("address", ())
                if socket[0] == "local":
                    master_site = site
            if external_sites:
                error_collector = {}
                successful = []
                client = paramiko.SSHClient()
                client.load_system_host_keys()
                for external_site, site_ip in external_sites.items():
                    try:
                        client.connect(
                            hostname=site_ip[0], port=22, username=external_site, timeout=5
                        )
                        sftp_cli = client.open_sftp()
                        sftp_cli.put(
                            localpath=CONFIG_FILE_STR,
                            remotepath=CONFIG_FILE_STR.replace(master_site, external_site),
                        )
                        sftp_cli.close()
                        client.close()
                        successful.append(external_site)
                    except Exception as exc:
                        error_collector[site] = str(exc)
                if error_collector:
                    for s, excep in external_sites.items():
                        flash(
                            f"Site <b>{s}</b> could not get file, reason: <b>{excep}</b>",
                            msg_type="error",
                        )
                if successful:
                    flash(
                        f"Config was successfully copied to the following sites: <b>{', '.join(successful)}</b>",
                        msg_type="message",
                    )
            html.reload_whole_page()
            user.set_rowselection(selection_id(), "carrier", selection, "set")
    else:
        user.set_rowselection(selection_id(), "carrier", [], "set")


def _page_menu_entries_ack_all_werks() -> Iterator[PageMenuEntry]:

    yield PageMenuEntry(
        title=_("Save Config"),
        icon_name="werk_ack",
        is_shortcut=True,
        is_suggested=True,
        item=make_simple_link(
            make_confirm_delete_link(
                url=makeactionuri(
                    request, transactions, [("_safe_config", "1"), ("selection_id", selection_id())]
                ),
                title=_("Save Configuration"),
                confirm_button=_("Save"),
            )
        ),
        # is_enabled=bool(unacknowledged_incompatible_werks()),
    )
    # sites.live().set_prepend_site(True)
    # only_contact = []
    # for site, contact_group_title, user, contact in sites.live().query("GET contactgroups\n"):
    #     if contact == "name" or contact == "all" or contact in only_contact:
    #         continue
    #     only_contact.append(contact)
    for contact, contact_group_title in get_usable_contact_groups().items():
        yield PageMenuEntry(
            title=_(f"Send Test SMS to {contact_group_title}"),
            icon_name="bell",
            is_shortcut=True,
            is_suggested=True,
            item=make_simple_link(
                make_confirm_delete_link(
                    url=makeactionuri(request, transactions, [("_send_sms", contact)]),
                    title=_(f"Send Test SMS to {contact_group_title}"),
                    confirm_button=_("send"),
                )
            ),
            # is_enabled=bool(unacknowledged_incompatible_werks()),
        )


@cmk.gui.pages.page_registry.register_page("sms_mega_site")
class ModeChangeLogPage(cmk.gui.pages.Page):
    def _title(self) -> str:
        return _("SMS Settings")

    def page(self) -> cmk.gui.pages.PageResult:

        breadcrumb = make_simple_page_breadcrumb(mega_menu_registry["help_links"], self._title())

        make_header(
            html,
            self._title(),
            breadcrumb,
            self._page_menu(breadcrumb),
        )

        for message in get_flashed_messages(with_categories=True):
            if message.msg_type == "error":
                html.open_div(class_=["warning"])
                html.write_text(message.msg)
                html.close_div()
            else:
                html.show_message(message.msg)

        handle_acknowledgement()

        config_dict, _contact_groups_title = inital_read()
        row_config_selected = []
        for contact_group, names in config_dict.items():
            for user_name, status in names.items():
                if status:
                    row_config_selected.append(f"_cb_{contact_group}--{user_name}")

        user.set_rowselection(selection_id(), "carrier", row_config_selected, "set")
        html.open_div(class_="wato")
        html.open_form()
        forms.section()
        sms_table()
        forms.section_close()
        html.close_form()
        html.close_div()
        html.footer()
        html.hidden_field("selection_id", selection_id())
        html.hidden_fields()
        init_rowselect("carrier")

    def _page_menu(self, breadcrumb: Breadcrumb) -> PageMenu:
        return PageMenu(
            dropdowns=[
                PageMenuDropdown(
                    name="options",
                    title=_("Options"),
                    topics=[
                        PageMenuTopic(
                            title=_("Possible Options"),
                            entries=list(_page_menu_entries_ack_all_werks()),
                        ),
                    ],
                ),
            ],
            breadcrumb=breadcrumb,
        )

    def action(self) -> None:
        handle_acknowledgement()
