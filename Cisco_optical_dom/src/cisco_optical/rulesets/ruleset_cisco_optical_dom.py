from cmk.rulesets.v1 import Help, Label, Title
from cmk.rulesets.v1.form_specs import (
    BooleanChoice,
    DefaultValue,
    DictElement,
    Dictionary,
    Float,
    LevelDirection,
    LevelsType,
    SimpleLevels,
)
from cmk.rulesets.v1.rule_specs import (
    CheckParameters,
    DiscoveryParameters,
    HostAndItemCondition,
    Topic,
)


def _check_parameter_form() -> Dictionary:
    return Dictionary(
        help_text=Help(
            "Configure RX/TX optical power thresholds. Custom Checkmk levels "
            "override thresholds reported by CISCO-OPTICAL-MIB."
        ),
        elements={
            "use_device_thresholds": DictElement(
                parameter_form=BooleanChoice(
                    title=Title("Use device thresholds as fallback"),
                    label=Label("Use thresholds reported by CISCO-OPTICAL-MIB"),
                    prefill=DefaultValue(True),
                ),
                required=True,
            ),
            "rx_lower": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("RX power lower levels"),
                    form_spec_template=Float(unit_symbol="dBm"),
                    level_direction=LevelDirection.LOWER,
                    prefill_levels_type=DefaultValue(LevelsType.NONE),
                    prefill_fixed_levels=DefaultValue((-11.0, -13.0)),
                ),
                required=True,
            ),
            "rx_upper": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("RX power upper levels"),
                    form_spec_template=Float(unit_symbol="dBm"),
                    level_direction=LevelDirection.UPPER,
                    prefill_levels_type=DefaultValue(LevelsType.NONE),
                    prefill_fixed_levels=DefaultValue((3.0, 5.0)),
                ),
                required=True,
            ),
            "tx_lower": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("TX power lower levels"),
                    form_spec_template=Float(unit_symbol="dBm"),
                    level_direction=LevelDirection.LOWER,
                    prefill_levels_type=DefaultValue(LevelsType.NONE),
                    prefill_fixed_levels=DefaultValue((-7.0, -9.0)),
                ),
                required=True,
            ),
            "tx_upper": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("TX power upper levels"),
                    form_spec_template=Float(unit_symbol="dBm"),
                    level_direction=LevelDirection.UPPER,
                    prefill_levels_type=DefaultValue(LevelsType.NONE),
                    prefill_fixed_levels=DefaultValue((3.0, 5.0)),
                ),
                required=True,
            ),
        },
    )


def _discovery_parameter_form() -> Dictionary:
    return Dictionary(
        help_text=Help(
            "By default a Cisco Optical DOM service is discovered only when the "
            "associated traffic interface (for example HundredGigE or FourHundredGigE) "
            "has IF-MIB ifAdminStatus=up and ifOperStatus=up. The Optics pseudo-interface "
            "itself is not used as the authoritative state."
        ),
        elements={
            "discover_only_up": DictElement(
                parameter_form=BooleanChoice(
                    title=Title("Discover only active traffic interfaces"),
                    label=Label("Require the associated data interface to be admin/oper up"),
                    prefill=DefaultValue(True),
                ),
                required=True,
            ),
        },
    )


rule_spec_cisco_optical_dom = CheckParameters(
    name="cisco_optical_dom",
    title=Title("Cisco Optical DOM"),
    topic=Topic.NETWORKING,
    parameter_form=_check_parameter_form,
    condition=HostAndItemCondition(item_title=Title("Optical interface")),
)


rule_spec_cisco_optical_dom_discovery = DiscoveryParameters(
    name="cisco_optical_dom_discovery",
    title=Title("Cisco Optical DOM discovery"),
    topic=Topic.NETWORKING,
    parameter_form=_discovery_parameter_form,
)
