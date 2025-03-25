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


def _parameter_form_dell_emc_ml3_drive() -> Dictionary:
    return Dictionary(
        elements={
            "cleaning_needed": DictElement(
                required=False,
                parameter_form=ServiceState(
                    title=Title("Status when Device cleaning needed"),
                    prefill=DefaultValue(ServiceState.WARN),
                ),
            ),
            "ava_map": DictElement(
                parameter_form=Dictionary(
                    title=Title("Available Status translation"),
                    elements={
                        "ava_map_1": DictElement(
                            required=True,
                            parameter_form=ServiceState(
                                title=Title("other"), prefill=DefaultValue(ServiceState.WARN)
                            ),
                        ),
                        "ava_map_2": DictElement(
                            required=True,
                            parameter_form=ServiceState(
                                title=Title("unknown"), prefill=DefaultValue(ServiceState.UNKNOWN)
                            ),
                        ),
                        "ava_map_3": DictElement(
                            required=True,
                            parameter_form=ServiceState(
                                title=Title("runningFullPower"),
                                prefill=DefaultValue(ServiceState.OK),
                            ),
                        ),
                        "ava_map_4": DictElement(
                            required=True,
                            parameter_form=ServiceState(
                                title=Title("warning"), prefill=DefaultValue(ServiceState.WARN)
                            ),
                        ),
                        "ava_map_5": DictElement(
                            required=True,
                            parameter_form=ServiceState(
                                title=Title("inTest"), prefill=DefaultValue(ServiceState.WARN)
                            ),
                        ),
                        "ava_map_6": DictElement(
                            required=True,
                            parameter_form=ServiceState(
                                title=Title("notApplicable"),
                                prefill=DefaultValue(ServiceState.WARN),
                            ),
                        ),
                        "ava_map_7": DictElement(
                            required=True,
                            parameter_form=ServiceState(
                                title=Title("notApplicable"),
                                prefill=DefaultValue(ServiceState.WARN),
                            ),
                        ),
                        "ava_map_8": DictElement(
                            required=True,
                            parameter_form=ServiceState(
                                title=Title("offLine"),
                                prefill=DefaultValue(ServiceState.CRIT),
                            ),
                        ),
                        "ava_map_9": DictElement(
                            required=True,
                            parameter_form=ServiceState(
                                title=Title("offDuty"),
                                prefill=DefaultValue(ServiceState.WARN),
                            ),
                        ),
                        "ava_map_10": DictElement(
                            required=True,
                            parameter_form=ServiceState(
                                title=Title("degraded"), prefill=DefaultValue(ServiceState.CRIT)
                            ),
                        ),
                        "ava_map_11": DictElement(
                            required=True,
                            parameter_form=ServiceState(
                                title=Title("notInstalled"), prefill=DefaultValue(ServiceState.WARN)
                            ),
                        ),
                        "ava_map_12": DictElement(
                            required=True,
                            parameter_form=ServiceState(
                                title=Title("installError"), prefill=DefaultValue(ServiceState.CRIT)
                            ),
                        ),
                        "ava_map_13": DictElement(
                            required=True,
                            parameter_form=ServiceState(
                                title=Title("powerSaveUnknown"),
                                prefill=DefaultValue(ServiceState.WARN),
                            ),
                        ),
                        "ava_map_14": DictElement(
                            required=True,
                            parameter_form=ServiceState(
                                title=Title("powerSaveLowPowerMode"),
                                prefill=DefaultValue(ServiceState.WARN),
                            ),
                        ),
                        "ava_map_15": DictElement(
                            required=True,
                            parameter_form=ServiceState(
                                title=Title("powerSaveStandby"),
                                prefill=DefaultValue(ServiceState.WARN),
                            ),
                        ),
                        "ava_map_16": DictElement(
                            required=True,
                            parameter_form=ServiceState(
                                title=Title("powerCycle"), prefill=DefaultValue(ServiceState.WARN)
                            ),
                        ),
                        "ava_map_17": DictElement(
                            required=True,
                            parameter_form=ServiceState(
                                title=Title("powerSaveWarning"),
                                prefill=DefaultValue(ServiceState.WARN),
                            ),
                        ),
                        "ava_map_18": DictElement(
                            required=True,
                            parameter_form=ServiceState(
                                title=Title("paused"), prefill=DefaultValue(ServiceState.WARN)
                            ),
                        ),
                        "ava_map_19": DictElement(
                            required=True,
                            parameter_form=ServiceState(
                                title=Title("notReady"), prefill=DefaultValue(ServiceState.WARN)
                            ),
                        ),
                        "ava_map_20": DictElement(
                            required=True,
                            parameter_form=ServiceState(
                                title=Title("notConfigured"),
                                prefill=DefaultValue(ServiceState.WARN),
                            ),
                        ),
                        "ava_map_21": DictElement(
                            required=True,
                            parameter_form=ServiceState(
                                title=Title("quiesced"), prefill=DefaultValue(ServiceState.WARN)
                            ),
                        ),
                    },
                )
            ),
            "opa_map": DictElement(
                parameter_form=Dictionary(
                    title=Title("Operational Status translation"),
                    elements={
                        "opa_map_0": DictElement(
                            required=True,
                            parameter_form=ServiceState(
                                title=Title("unknown"), prefill=DefaultValue(ServiceState.UNKNOWN)
                            ),
                        ),
                        "opa_map_1": DictElement(
                            required=True,
                            parameter_form=ServiceState(
                                title=Title("other"), prefill=DefaultValue(ServiceState.WARN)
                            ),
                        ),
                        "opa_map_2": DictElement(
                            required=True,
                            parameter_form=ServiceState(
                                title=Title("ok"), prefill=DefaultValue(ServiceState.OK)
                            ),
                        ),
                        "opa_map_3": DictElement(
                            required=True,
                            parameter_form=ServiceState(
                                title=Title("degraded"),
                                prefill=DefaultValue(ServiceState.WARN),
                            ),
                        ),
                        "opa_map_4": DictElement(
                            required=True,
                            parameter_form=ServiceState(
                                title=Title("stressed"), prefill=DefaultValue(ServiceState.WARN)
                            ),
                        ),
                        "opa_map_5": DictElement(
                            required=True,
                            parameter_form=ServiceState(
                                title=Title("predictiveFailure"),
                                prefill=DefaultValue(ServiceState.WARN),
                            ),
                        ),
                        "opa_map_6": DictElement(
                            required=True,
                            parameter_form=ServiceState(
                                title=Title("error"),
                                prefill=DefaultValue(ServiceState.CRIT),
                            ),
                        ),
                        "opa_map_7": DictElement(
                            required=True,
                            parameter_form=ServiceState(
                                title=Title("non-RecoverableError"),
                                prefill=DefaultValue(ServiceState.CRIT),
                            ),
                        ),
                        "opa_map_8": DictElement(
                            required=True,
                            parameter_form=ServiceState(
                                title=Title("starting"),
                                prefill=DefaultValue(ServiceState.WARN),
                            ),
                        ),
                        "opa_map_9": DictElement(
                            required=True,
                            parameter_form=ServiceState(
                                title=Title("stopping"),
                                prefill=DefaultValue(ServiceState.WARN),
                            ),
                        ),
                        "opa_map_10": DictElement(
                            required=True,
                            parameter_form=ServiceState(
                                title=Title("stopped"), prefill=DefaultValue(ServiceState.WARN)
                            ),
                        ),
                        "opa_map_11": DictElement(
                            required=True,
                            parameter_form=ServiceState(
                                title=Title("inService"), prefill=DefaultValue(ServiceState.WARN)
                            ),
                        ),
                        "opa_map_12": DictElement(
                            required=True,
                            parameter_form=ServiceState(
                                title=Title("noContact"), prefill=DefaultValue(ServiceState.CRIT)
                            ),
                        ),
                        "opa_map_13": DictElement(
                            required=True,
                            parameter_form=ServiceState(
                                title=Title("lostCommunication"),
                                prefill=DefaultValue(ServiceState.WARN),
                            ),
                        ),
                        "opa_map_14": DictElement(
                            required=True,
                            parameter_form=ServiceState(
                                title=Title("aborted"),
                                prefill=DefaultValue(ServiceState.WARN),
                            ),
                        ),
                        "opa_map_15": DictElement(
                            required=True,
                            parameter_form=ServiceState(
                                title=Title("dormant"),
                                prefill=DefaultValue(ServiceState.WARN),
                            ),
                        ),
                        "opa_map_16": DictElement(
                            required=True,
                            parameter_form=ServiceState(
                                title=Title("supportingEntityInError"),
                                prefill=DefaultValue(ServiceState.CRIT),
                            ),
                        ),
                        "opa_map_17": DictElement(
                            required=True,
                            parameter_form=ServiceState(
                                title=Title("completed"),
                                prefill=DefaultValue(ServiceState.OK),
                            ),
                        ),
                        "opa_map_18": DictElement(
                            required=True,
                            parameter_form=ServiceState(
                                title=Title("powerMode"),
                                prefill=DefaultValue(ServiceState.WARN),
                            ),
                        ),
                        "opa_map_19": DictElement(
                            required=True,
                            parameter_form=ServiceState(
                                title=Title("dMTFReserved"),
                                prefill=DefaultValue(ServiceState.WARN),
                            ),
                        ),
                    },
                )
            ),
        }
    )


rule_spec_audiocodes_system_events = CheckParameters(
    name="dell_emc_ml3_drive",
    topic=Topic.APPLICATIONS,
    title=Title("TapeLibrary Dell/EMC ML3 Status"),
    condition=HostAndItemCondition(item_title=Title("Tape Drive")),
    parameter_form=_parameter_form_dell_emc_ml3_drive,
)
