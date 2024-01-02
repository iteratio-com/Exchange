#!/usr/bin/env python3

# 2023, marcus.klein@iteratio.com

from cmk.gui.i18n import _
from cmk.gui.plugins.wato.utils import (
    CheckParameterRulespecWithItem,
    DropdownChoice,
    RulespecGroupCheckParametersEnvironment,
    rulespec_registry,
)
from cmk.gui.valuespec import Dictionary, Integer, MonitoringState, TextInput, Tuple


def _item_spec_hmip_shuttercontactmagnetic() -> str:
    return TextInput(
        title=_("Name of the magnetic shutter contact"),
        allow_empty=True,
    )


def _parameter_valuespec_hmip_shuttercontactmagnetic() -> Dictionary:
    return Dictionary(
        elements=[
            (
                "windowstate",
                DropdownChoice(
                    title=_("Expected state of the shutter contact"),
                    help=_("Expected state of the shutter contact"),
                    choices=[
                        ("CLOSED", _("Closed")),
                        ("OPEN", _("Open")),
                    ],
                    default_value="CLOSED",
                ),
            ),
            (
                "windowstate_mon_state",
                MonitoringState(
                    default_value=2,
                    title=_("Service state for different window state"),
                    help=_(
                        "Service state in case the shutter contact has another state than expected"
                    ),
                ),
            ),
            (
                "rssi",
                Tuple(
                    title=_("RSSI Value"),
                    elements=[
                        Integer(title=_("Warning if less or equal than"), default_value=-85),
                        Integer(title=_("Critical if less or equal than"), default_value=-90),
                    ],
                    help=_("RSSI Value of zigbee connection from shutter contact to access point"),
                ),
            ),
        ],
    )


rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name="homematicip_shuttercontactmagnetic",
        group=RulespecGroupCheckParametersEnvironment,
        item_spec=_item_spec_hmip_shuttercontactmagnetic,
        parameter_valuespec=_parameter_valuespec_hmip_shuttercontactmagnetic,
        title=lambda: _("HomematicIP Magnetic Shutter Contact"),
    )
)
