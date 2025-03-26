#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cmk.rulesets.v1 import Title
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    ServiceState,
)
from cmk.rulesets.v1.rule_specs import CheckParameters, HostAndItemCondition, Topic


def _parameter_form_damocles2_inputs_group() -> Dictionary:
    return Dictionary(
        elements={
            "alert_state": DictElement(
                required=True,
                parameter_form=ServiceState(
                    title=Title("State when Alert State reached"),
                    prefill=DefaultValue(ServiceState.CRIT),
                ),
            ),
        }
    )


rule_spec_audiocodes_system_events = CheckParameters(
    name="damocles2_inputs_group",
    topic=Topic.ENVIRONMENTAL,
    title=Title("Damocles2/Poseidon2 Inputs Alert State"),
    condition=HostAndItemCondition(item_title=Title("Name of Input Sensor")),
    parameter_form=_parameter_form_damocles2_inputs_group,
)
