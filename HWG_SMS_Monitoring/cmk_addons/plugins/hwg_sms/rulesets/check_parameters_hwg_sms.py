#!/usr/bin/env python3

from cmk.rulesets.v1 import Title
from cmk.rulesets.v1.form_specs import (
    DictElement,
    Dictionary,
    DefaultValue,
    LevelDirection,
    Percentage,
    SimpleLevels,
    Integer,
)
from cmk.rulesets.v1.rule_specs import CheckParameters, HostCondition, Topic


def _parameter_form_sms_gw_signal() -> Dictionary:
    return Dictionary(
        elements={
            "signal_quality": DictElement(
                required=False,
                parameter_form=SimpleLevels(
                    title=Title("Set Levels on Signal Quality (lower)"),
                    form_spec_template=Percentage(),
                    level_direction=LevelDirection.LOWER,
                    prefill_fixed_levels=DefaultValue((30.0, 10.0)),
                ),
            ),
            "signal_strength": DictElement(
                required=False,
                parameter_form=SimpleLevels(
                    title=Title("Set Levels on Signal Strength (lower)"),
                    form_spec_template=Integer(unit_symbol="dBm"),
                    level_direction=LevelDirection.LOWER,
                    prefill_fixed_levels=DefaultValue((-85, -95)),
                ),
            ),
        }
    )


rule_spec_sms_gw_signal = CheckParameters(
    name="sms_gw_signal",
    topic=Topic.APPLICATIONS,
    parameter_form=_parameter_form_sms_gw_signal,
    title=Title("HWG SMS Signal Levels"),
    condition=HostCondition(),
)
