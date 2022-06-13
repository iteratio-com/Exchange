#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

import cmk.gui.bi as bi
import cmk.gui.watolib as watolib
from cmk.gui.exceptions import MKUserError
from cmk.gui.i18n import _
from cmk.gui.plugins.wato import (
    IndividualOrStoredPassword,
    RulespecGroup,
    monitoring_macro_help,
    rulespec_group_registry,
    rulespec_registry,
    HostRulespec,
)
from cmk.gui.valuespec import (
    ID,
    Age,
    Alternative,
    CascadingDropdown,
    Checkbox,
    Dictionary,
    DropdownChoice,
    FixedValue,
    Float,
    HTTPUrl,
    Integer,
    ListChoice,
    ListOf,
    ListOfStrings,
    MonitoringState,
    Password,
    RegExp,
    RegExpUnicode,
    TextAscii,
    TextUnicode,
    Transform,
    Tuple,
)
from cmk.gui.plugins.wato.utils import (
    PasswordFromStore, )
from cmk.utils import aws_constants

from cmk.gui.plugins.wato.datasource_programs import (
    RulespecGroupDatasourcePrograms)


def _factory_default_special_agent_pihole():
    # No default, do not use setting if no rule matches
    return watolib.Rulespec.FACTORY_DEFAULT_UNUSED


def _valuespec_special_agent_pihole():
    return Dictionary(
        title=_("Monitor Pi-Hole, via API"),
        help=
        _("This rule selects the Pi-Hole Special agent, which uses the API to gather information "
          "about connections (blocked etc), status, version and custom DNS entries via the HW/SW inventory."
          "All Options are optional, since some confi"),
        optional_keys=[
            "no-cert-check", "token", "timeout", "protocol", 'piggyhost',
            'user', 'address'
        ],
        elements=[
            (
                "address",
                TextAscii(
                    title=_("Use differend Hostaddress insted of IP-address"),
                    #regex="[a-zA-Z_0-9_.-:$\/]",
                    #regex_error=_("Specify here a url"),
                    help=
                    _("Here you can specify everything which is between http://<tt>HERE</tt>/API... You can also fillin <tt>$HOSTNAME$</tt> if you just want the script to fill in the Hostname"
                      ))),
            ("token",
             IndividualOrStoredPassword(title=_("API-Token"),
                                        allow_empty=True)),
            ("protocol",
             DropdownChoice(title=_("Protocol to Connect to API"),
                            choices=[
                                (_("https"), _("Https")),
                                (_("http"), _("Http")),
                            ],
                            default_value=_("http"))),
            ("no-cert-check",
             DropdownChoice(title=_("SSL certificate verification"),
                            choices=[
                                (True, _("Activiate")),
                                (False, _("Deactivate")),
                            ],
                            default_value=False)),
            ("timeout",
             Integer(title=_("Timeout for Query calls"),
                     default_value=10,
                     unit="s")),
            (
                "piggyhost",
                TextAscii(
                    title=_("Give Host Piggyback-Informations"),
                    #regex="[a-zA-Z_0-9_.-]",
                    #regex_error=_("Specify here the a hostname within Checkmk"),
                    help=
                    _("Informations of the Special-Agent can be passed to a different Host"
                      ),
                ))
        ],
    )


rulespec_registry.register(
    HostRulespec(
        factory_default=_factory_default_special_agent_pihole(),
        group=RulespecGroupDatasourcePrograms,
        name="special_agents:pihole",
        valuespec=_valuespec_special_agent_pihole,
    ))
