#!/usr/bin/env python3

# 2023, marcus.klein@iteratio.com

from cmk.gui.i18n import _
from cmk.gui.plugins.wato.special_agents.common import RulespecGroupDatasourceProgramsHardware
from cmk.gui.plugins.wato.utils import HostRulespec, IndividualOrStoredPassword, rulespec_registry
from cmk.gui.valuespec import Dictionary, DualListChoice, TextInput
from cmk.gui.watolib.rulespecs import Rulespec


def _factory_default_special_agents_hmip():
    # No default, do not use setting if no rule matches
    return Rulespec.FACTORY_DEFAULT_UNUSED


def _valuespec_special_agents_hmip():
    return Dictionary(
        title=_("HomematicIP"),
        help=_("This rule is used to set up HomematicIP Special agent."),
        elements=[
            (
                "access_point",
                TextInput(
                    title=_("Access Point SGTIN"),
                    help=_("Access Point SGTIN can be found on the back of the device."),
                    default_value="4F35BC689C427451C9748098",
                    size=29,
                    regex="^[0-9A-F\-]{24,29}$",
                    regex_error=_(
                        "Please enter a valid Access Point SGTIN (24 hex chars, can be separated with up to 5 dashes): e.g. <tt>4F35-BC68-9C42-7451-C974-8098</tt>"
                    ),
                ),
            ),
            (
                "auth_token",
                IndividualOrStoredPassword(
                    title=_("Auth Token"),
                    help=_(
                        "Auth Token can be generated with <tt>$OMD_ROOT/local/lib/python3/bin/hmip_generate_auth_token.py</tt>"
                    ),
                ),
            ),
            (
                "device_types",
                DualListChoice(
                    title=_("Device Types"),
                    choices=[
                        ("HeatingThermostat", _("Heating Thermostat")),
                        # ("PlugableSwitchMeasuring", _("Plugable Switch Measuring")),
                        # ("ShutterContact", _("Shutter Contact")),
                        # (
                        #     "TemperatureHumiditySensorDisplay",
                        #     _("Temperature Humidity Sensor Display"),
                        # ),
                        # ("WallMountedThermostatPro", _("Wall Mounted Thermostat Pro")),
                        # ("WaterSensor", _("Water Sensor")),
                    ],
                    help=_(
                        "Select the device types to be monitored, default are all device types."
                    ),
                    rows=8,
                ),
            ),
        ],
        required_keys=["access_point", "auth_token"],
    )


rulespec_registry.register(
    HostRulespec(
        factory_default=_factory_default_special_agents_hmip(),
        group=RulespecGroupDatasourceProgramsHardware,
        name="special_agents:hmip",
        valuespec=_valuespec_special_agents_hmip,
    )
)
