#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cmk.gui.watolib as watolib

from cmk.gui.plugins.wato import (
    CheckParameterRulespecWithoutItem,
    RulespecGroupCheckParametersOperatingSystem,
    rulespec_registry,
    HostRulespec,
    ServiceRulespec,
)

from cmk.gui.valuespec import (
    Dictionary,
    DropdownChoice,
    Integer,
    TextAscii,
    ListChoice,
    Integer,
    Transform,
    RegExp,
    RegExpUnicode,
    Tuple,
    Age,
    MonitoringState,
)

def _valuespec_wsus_next_reboot():
        return Dictionary(
            elements=
            [("downtime_comment",
                    TextInput(
                        title=_("Downtime comment"),
                        help=
                        _("Comment for downtimes"),
                        default_value="WSUS set downtime",
                        regex="^[a-zA-Z0-9~\-_ ]*$",
                        regex_error=
                        _("<tt>a-z0-9~\-_ </tt> are allowed chars."),
                    ),
                ),
            ("downtime_author",
                    TextInput(
                        title=_("Downtime author"),
                        help=_("Author for downtimes"),
                        default_value="automation",
                        regex="^[a-zA-Z0-9~\-_]*$",
                        regex_error=_("<tt>a-z0-9~\-_</tt> are allowed chars."),
                    ),
                ),
            ("downtime_duration",
                    Age(
                        title=_("Downtime duration"),
                        help=_("Downtime duration"),
                        default_value=7200,
                        display=["hours","minutes"],
                    ),
                ),
            ("default_state",
                    MonitoringState(
                        title=_("Service state for unset update registry informations"),
                        help=_("Service state for unset update registry informations"),
                        default_value=1,
                    ))

                ],
            title=_("WSUS next reboot"),
            help=
            _("This rule is used to configure the settings for <i>WSUS set downtimes</i> according to host registry data."
              ),
        )


rulespec_registry.register(
    CheckParameterRulespecWithoutItem(
        check_group_name="wsus_next_reboot",
        group=RulespecGroupCheckParametersOperatingSystem,
        match_type="dict",
        parameter_valuespec=_valuespec_wsus_next_reboot,
        title=lambda: _("WSUS next reboot"),
    ))
