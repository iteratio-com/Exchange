#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

from cmk.gui.i18n import _
from cmk.gui.valuespec import (
    Dictionary,
    TextAscii,
    TextUnicode,
    DropdownChoice,
)

from cmk.gui.plugins.wato import (
    rulespec_group_registry,
    RulespecGroup,
    rulespec_registry,
    HostRulespec,
    IndividualOrStoredPassword,
)


@rulespec_group_registry.register
class RulespecGroupIntegrateOtherServices(RulespecGroup):
    @property
    def name(self):
        return "custom_checks"

    @property
    def title(self):
        return _("Other services")

    @property
    def help(self):
        return _("This services are provided by so called active checks. "
                 "You can also integrate custom nagios plugins.")


def _valuespec_active_checks_radius():
    return Dictionary(
        title=_("Check Radius Server"),
        help=_(
            "This check connects to the specified radius server, sends a custom request "
            "and checks that the server accepts the request "
            "This check uses the active check <tt>check_radius</tt>."),
        optional_keys=[
            "type",
            "dict",
        ],
        elements=[
            ("description",
             TextUnicode(
                 title=_("Service Description"),
                 help=_("The name of this active service to be displayed."),
                 allow_empty=False,
             )),
            ("secret",
             IndividualOrStoredPassword(title=_("Radius secret"),
                                        allow_empty=False,
                                        help=_('secret key'))),
            ("nasid",
             TextAscii(title=_("Nas-ID"),
                       allow_empty=False,
                       help=_('Nas-ID of Client'))),
            ("user",
             TextAscii(
                 title=_("Radius User"),
                 allow_empty=False,
                 help=_('The username used to connect to the radius server'))),
            ("password",
             IndividualOrStoredPassword(
                 title=_("Password of Radius Client"),
                 allow_empty=False,
                 help=_('The password used to connect to the radius server'))),
            (
                "type",
                DropdownChoice(
                    title=_("NAS-Port-Type"),
                    choices=[
                        ("19", _("Wireless")),
                        ("17", _("Cable")),
                        ("5", _("Virtual")),
                    ],
                    default_value="19",
                ),
            ),
            ("dict",
             TextAscii(
                 title=_("Dictionary File"),
                 allow_empty=True,
                 default_value="~/local/lib/nagios/plugins/dictionary",
                 help=
                 _('Full Path and File name of Dictionary File. If not set the check will look into <tt>SITEHOME/local/lib/nagios/plugins/dictionary</tt>.'
                   ))),
        ])


rulespec_registry.register(
    HostRulespec(
        group=RulespecGroupIntegrateOtherServices,
        match_type="all",
        name="active_checks:radius",
        valuespec=_valuespec_active_checks_radius,
    ))