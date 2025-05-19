#!/usr/bin/env python3

from cmk.gui.i18n import _, _l
from cmk.gui.main_menu import mega_menu_registry
from cmk.gui.type_defs import MegaMenu, TopicMenuItem, TopicMenuTopic

# location of this script local/lib/check_mk/gui/plugins/wato/NAME.py
# Icons from checkmk/web/htdocs/images/icons/


def _kplus_help_menu_topics() -> list[TopicMenuTopic]:
    return [
        TopicMenuTopic(
            name="kplus_help",
            title=_("kplus documents"),
            icon=None,
            items=[
                TopicMenuItem(
                    name="kplus_password_store",
                    title=_("SMS Settings"),
                    url="sms_mega_site.py",
                    sort_index=10,
                    icon="security",
                ),
            ],
        ),
    ]


mega_menu_registry.register(
    MegaMenu(
        name="help_kplus_links",
        title=_l("kplus"),
        icon="main_help",
        sort_index=17,
        topics=_kplus_help_menu_topics,
        info_line=lambda: "kplus documentation",
    )
)
