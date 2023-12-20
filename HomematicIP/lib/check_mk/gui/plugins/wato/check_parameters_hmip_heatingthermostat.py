#!/usr/bin/env python3

# 2023, marcus.klein@iteratio.com

from cmk.gui.i18n import _
from cmk.gui.plugins.wato.utils import (
    CheckParameterRulespecWithItem,
    RulespecGroupCheckParametersEnvironment,
    rulespec_registry,
)
from cmk.gui.valuespec import Dictionary, Float, Integer, MonitoringState, TextInput, Tuple


def _item_spec_hmip_thermostat() -> str:
    return TextInput(
        title=_("Name of the thermostat"),
        allow_empty=True,
    )


temperaturetpl = [
    (
        "upper",
        Tuple(
            title=_("Upper Temperature Levels"),
            elements=[
                Float(title=_("Warning at"), unit="°C", default_value=26),
                Float(title=_("Critical at"), unit="°C", default_value=30),
            ],
        ),
    ),
    (
        "lower",
        Tuple(
            title=_("Lower Temperature Levels"),
            elements=[
                Float(title=_("Warning below"), unit="°C", default_value=15),
                Float(title=_("Critical below"), unit="°C", default_value=12),
            ],
        ),
    ),
]


def _parameter_valuespec_hmip_thermostat() -> Dictionary:
    return Dictionary(
        elements=[
            (
                "valveactualtemperature",
                Dictionary(
                    title=_("Valve environment sensor temperature"),
                    elements=temperaturetpl,
                    help=_("Valve environment sensor temperature in °C"),
                ),
            ),
            (
                "setpointtemperature",
                Dictionary(
                    title=_("Set temperature for room"),
                    elements=temperaturetpl,
                    help=(_("The current temperature which should be reached in the room in °C")),
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
                    help=_("RSSI Value of zigbee connection from thermostat to access point"),
                ),
            ),
            (
                "configpending",
                MonitoringState(
                    default_value=1,
                    title=_("State pending configuration"),
                    help=_("State in case the thermostat has a pending configuration"),
                ),
            ),
            (
                "dutycycle",
                MonitoringState(
                    default_value=1,
                    title=_("State duty cycle"),
                    help=(_("State in case duty cycle is active")),
                ),
            ),
            (
                "lowbattery",
                MonitoringState(
                    default_value=2,
                    title=_("State low battery"),
                    help=(_("State in case the thermostat's battery is low")),
                ),
            ),
            (
                "unreach",
                MonitoringState(
                    default_value=2,
                    title=_("State unreachable"),
                    help=(_("State in case the thermostat is unreachable")),
                ),
            ),
            (
                "operationlock",
                MonitoringState(
                    default_value=0,
                    title=_("State operation lock"),
                    help=(_("State in case the thermostat is locked for operation")),
                ),
            ),
            (
                "valvestate",
                MonitoringState(
                    default_value=2,
                    title=_("State valve state"),
                    help=(_("State in case the valve is not in 'adaptation done' state")),
                ),
            ),
        ],
    )


rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name="homematicip_heatingthermostat",
        group=RulespecGroupCheckParametersEnvironment,
        item_spec=_item_spec_hmip_thermostat,
        parameter_valuespec=_parameter_valuespec_hmip_thermostat,
        title=lambda: _("HomematicIP Thermostat"),
    )
)
