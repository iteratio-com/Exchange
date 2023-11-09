#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cmk.gui.i18n import _
from cmk.gui.plugins.wato.utils import (
    CheckParameterRulespecWithoutItem,
    rulespec_registry,
    RulespecGroupCheckParametersNetworking,
)
from cmk.gui.valuespec import (
    Dictionary,
    Integer,
    MonitoringState,
)


def _parameter_valuespec_sms_gw_signal():
    return Dictionary(
        elements=[
            (
                "synceinteraces",
                Integer(
                    title=_("Amount of Sync-E Interfaces"),
                    help=_(
                        "Set here the number of Interfaces (Ethernet), which should be configured for using Sync-E "
                        "(Number of Interfaces >= this Parameter))."
                    ),
                    default_value=2,
                ),
            ),
            (
                "state_amound_interfaces",
                MonitoringState(
                    title=_("Status if incorrect number of interfaces"),
                    help=_("Status if the value is below 2 or the value of the parameter above."),
                    default_value=1,
                ),
            ),
            (
                "state_interface_changed",
                MonitoringState(
                    title=_("Status if the selected Interface changed"),
                    help=_("State if the Selected Sync-E Interface changed."),
                    default_value=2,
                ),
            ),
        ],
        optional_keys=["state_amound_interfaces", "state_interface_changed", "synceinteraces"],
        ignored_keys=["discovered_selected"],
    )


rulespec_registry.register(
    CheckParameterRulespecWithoutItem(
        check_group_name="cisco_sync_e_group",
        group=RulespecGroupCheckParametersNetworking,
        match_type="dict",
        parameter_valuespec=_parameter_valuespec_sms_gw_signal,
        title=lambda: _("Cisco Sync-E Interfaces Levels"),
    )
)
