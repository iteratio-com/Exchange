#!/usr/bin/env python3

from cmk.gui.i18n import _
from cmk.gui.plugins.wato.utils import (
    IndividualOrStoredPassword,
    NotificationParameter,
    notification_parameter_registry,
)
from cmk.gui.valuespec import Dictionary, Integer, TextInput


@notification_parameter_registry.register
class NotificationParameterHWG_SMS(NotificationParameter):
    @property
    def ident(self) -> str:
        return "hwg_notification"

    @property
    def spec(self):
        return Dictionary(
            title=_("Create notification with the following parameters"),
            help=_(
                "Configure here the parameters for the notification to the HWG SMS Modem. (see. https://www.hw-group.com/support/how-to-send-sms-via-hwg-sms-gw3 for more information)."
            ),
            optional_keys=["timeout", "sms_backup_url", "host_subject", "service_subject"],
            elements=[
                (
                    "sms_url",
                    TextInput(
                        title=_("Modem URL"),
                        help=_(
                            "Configure your modem IPAddress (HTTP and service.xml will be added)."
                        ),
                        allow_empty=False,
                    ),
                ),
                (
                    "sms_backup_url",
                    TextInput(
                        title=_("Modem URL for Backup"),
                        help=_(
                            "Configure your modem IPAddress (HTTP and service.xml will be added). "
                            "The Backup Modem is used when the first one is not reachable,"
                            " or has a result code (http) != 200 or the resulting SMS XML is != 1."
                        ),
                    ),
                ),
                (
                    "sms_user",
                    TextInput(
                        title=_("Username"),
                        help=_("The user, used for login."),
                        size=40,
                        allow_empty=False,
                    ),
                ),
                (
                    "sms_password",
                    IndividualOrStoredPassword(
                        title=_("Password of the user"),
                        allow_empty=False,
                    ),
                ),
                (
                    "host_subject",
                    TextInput(
                        title=_("Subject for host notifications"),
                        help=_(
                            "Here you are allowed to use all macros that are defined in the "
                            "notification context. Were as LASTHOSTSTATECHANGE will calculated in localtime."
                        ),
                        default_value="$LASTHOSTSTATECHANGE$ - $HOSTNAME$ - $EVENT_TXT$",
                        size=90,
                    ),
                ),
                (
                    "service_subject",
                    TextInput(
                        title=_("Subject for service notifications"),
                        help=_(
                            "Here you are allowed to use all macros that are defined in the "
                            "notification context. Were as LASTSERVICESTATECHANGE will calculated in localtime."
                        ),
                        default_value="$LASTSERVICESTATECHANGE$ - $HOSTNAME$/$SERVICEDESC$ $EVENT_TXT$",
                        size=90,
                    ),
                ),
                (
                    "timeout",
                    Integer(
                        title=_("Set optional timeout for connections to the modem."),
                        help=_("Here you can configure timeout settings."),
                        default_value=10,
                    ),
                ),
            ],
        )
