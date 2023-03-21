#!/usr/bin/env python3

from cmk.gui.valuespec import (
    Dictionary,
    DropdownChoice,
    Integer,
    ListOfStrings,
    TextUnicode,
    TextInput,
)

from cmk.gui.i18n import _
from cmk.gui.plugins.wato.utils import (
    IndividualOrStoredPassword,
    notification_parameter_registry,
    NotificationParameter,
)

import socket

TMPL_HOST_SUBJECT = "Check_MK: $HOSTNAME$ - $EVENT_TXT$"
TMPL_SERVICE_SUBJECT = "Check_MK: $HOSTNAME$/$SERVICEDESC$ $EVENT_TXT$"


@notification_parameter_registry.register
class NotificationILert(NotificationParameter):
    @property
    def ident(self) -> str:
        return "cordaware_bestinformed"

    @property
    def spec(self):
        return Dictionary(
            title=_("Create notification Cordaware bestinformed with the following parameters"),
            required_keys=["api_url", "api_user", "api_key"],
            elements=[
                ("api_url",
                 TextInput(
                     title=_("API Url of bestinformed with port"),
                     help=
                     _("Use this for specify the Cordaware bestinformed Host with Port, e.g. <tt>https://monitor:8431</tt>"
                      ),
                     regex="^(http|https)://.*",
                     regex_error=_("The URL must begin with <tt>http</tt> or <tt>https</tt>."),
                     size=64,
                     default_value="https://monitor:8431",
                 )),
                ("api_user",
                 TextInput(
                     title=_("API User"),
                     help=_("Fill here the user, e.g. <tt>rest_monitor</tt>."),
                     regex="rest_.*",
                     regex_error=_("User must begin with <tt>rest_</tt>."),
                 )),
                ("api_key",
                 IndividualOrStoredPassword(
                     title=_("API Secret (Token)"),
                     help=_("Fill here the toke for user specified above."),
                     size=32,
                 )),
                ("api_origin_host",
                 TextInput(
                     title=_("Origin Hostname (Checkmk Server)"),
                     help=
                     _("Fill here the Hostname of the Monitoring Hosts, e.g. Checkmk.Foo.Bar. If there is a need for a FQN. Default is the Hostname of the Monitoring Server."
                      ),
                     default_value=f"{socket.gethostname()}",
                     size=25,
                 )),
                ("api_ssl_verify",
                 DropdownChoice(title=_("Check HTTPS Certificate"),
                                choices=[("true", _("Enable Checking")),
                                         ("false", _("Disable checking"))],
                                default_value="false")),
                ("api_info_size",
                 DropdownChoice(title=_("Font Size of Info"),
                                help=_("Optionally set here the size of the font."),
                                choices=[("1", "1"), ("2", "2"), ("3", "3 (default)"), ("4", "4"),
                                         ("5", "5"), ("6", "6")],
                                default_value="3")),
                ("info_txt_host",
                 TextUnicode(
                     title=_("Info text for host notifications (Template)"),
                     help=_(
                         "Fill here the Syntax of the Message. All macros that are defined in the "
                         "notification context are Useable."),
                     default_value=TMPL_HOST_SUBJECT,
                     size=64,
                 )),
                ("info_txt_service",
                 TextUnicode(
                     title=_("Info text for service notifications (Template)"),
                     help=_(
                         "Fill here the Syntax of the Message. All macros that are defined in the "
                         "notification context are Useable."),
                     default_value=TMPL_SERVICE_SUBJECT,
                     size=64,
                 )),
                ("caption_txt_host",
                 TextUnicode(
                     title=_("Caption text for host notification (Template)"),
                     help=_(
                         "Template for Caption text for host notification. Usable are all macros that are defined in the "
                         "notification context."),
                     default_value="Check_MK: $HOSTNAME$ - $EVENT_TXT$",
                     size=64,
                 )),
                ("caption_txt_service",
                 TextUnicode(
                     title=_("Caption text for service notification (Template)"),
                     help=_(
                         "Template for Caption text for service notification. Usable are all macros that are defined in the "
                         "notification context."),
                     default_value="Check_MK: $HOSTNAME$ - $EVENT_TXT$",
                     size=64,
                 )),
                ("caption_txt_size",
                 DropdownChoice(title=_("Font Size of caption"),
                                help=_("Optionally set here the size of the font."),
                                choices=[("1", "1"), ("2", "2"), ("3", "3 (default)"), ("4", "4"),
                                         ("5", "5"), ("6", "6")],
                                default_value="3")),
                ("caption_txt_color",
                 TextUnicode(
                     title=_("Color of caption"),
                     help=_("Fill here the Color as Hex Code"),
                     default_value="FFFFFF",
                     size=7,
                 )),
                ("duration",
                 Integer(title=_("Duration of message"),
                         help=_("Fill here the Color as Hex Code"),
                         default_value="3",
                         unit="min")),
                ("active",
                 Integer(title=_("Active Time of message"),
                         help=_("Fill here the Color as Hex Code"),
                         default_value="5",
                         unit="min")),
                ("ldap_or_groups",
                 DropdownChoice(title=_("LDAP or Groups"),
                                help=_("Fill here the Color as Hex Code"),
                                choices=[("false", "False"), ("true", "True")],
                                default_value="false")),
                ("ldap_groups_text",
                 ListOfStrings(title=_("LDAP Groups text"),
                               help=_("Fill here the Color as Hex Code"),
                               default_value=["sich3cinform_test"])),
                ("filter",
                 ListOfStrings(title=_("Filters"),
                               help=_("Fill here the Color as Hex Code"),
                               default_value=["Alle Infoclients"])),
                ("info_background_caption",
                 TextUnicode(title=_("INFO Background Caption"),
                             help=_("Fill here the Color as Hex Code"),
                             default_value="CC0000")),
            ])
