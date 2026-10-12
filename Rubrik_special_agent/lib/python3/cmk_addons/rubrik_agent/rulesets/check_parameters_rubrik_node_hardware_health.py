"""Configure exceptions for unhealthy Rubrik hardware health policies."""

from collections.abc import Mapping, Sequence

from cmk.rulesets.v1 import Help, Label, Message, Title
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    List,
    SingleChoice,
    SingleChoiceElement,
)
from cmk.rulesets.v1.form_specs.validators import ValidationError
from cmk.rulesets.v1.rule_specs import CheckParameters, HostCondition, Topic


_POLICY_NAMES = (
    "DIMM_CHECKER",
    "DISK_CHECKER",
    "NETWORK_INTERFACE_CHECKER_PRIMARY",
    "NETWORK_INTERFACE_CHECKER_SECONDARY",
    "CHASSIS_CHECKER",
    "NODE_CHECKER",
    "P_S_U_CHECKER",
)


def _validate_unique_policies(value: Sequence[Mapping[str, object]]) -> None:
    names: list[str] = []
    for entry in value:
        name = entry["policy_name"]
        if not isinstance(name, str):
            raise ValidationError(Message("Policy names must be strings."))
        names.append(name)
    if len(names) != len(set(names)):
        raise ValidationError(Message("Each policy name may only be configured once."))


def _parameter_form() -> Dictionary:
    return Dictionary(
        elements={
            "policy_overrides": DictElement(
                parameter_form=List(
                    title=Title("Hardware health policy exceptions"),
                    help_text=Help(
                        "Exceptions apply only to unhealthy policies. Healthy policies remain OK. "
                        "Unconfigured unhealthy policies remain CRIT. The worst evaluated state "
                        "determines the service state; ignored findings remain visible in the details.",
                    ),
                    add_element_label=Label("Add policy exception"),
                    editable_order=False,
                    custom_validate=(_validate_unique_policies,),
                    element_template=Dictionary(
                        elements={
                            "policy_name": DictElement(
                                required=True,
                                parameter_form=SingleChoice(
                                    title=Title("Hardware health policy"),
                                    help_text=Help(
                                        "Select a known Rubrik hardware health policy. Policies not "
                                        "listed here are still monitored and remain CRIT when unhealthy.",
                                    ),
                                    elements=[
                                        SingleChoiceElement(name=name, title=Title(name))
                                        for name in _POLICY_NAMES
                                    ],
                                ),
                            ),
                            "handling": DictElement(
                                required=True,
                                parameter_form=SingleChoice(
                                    title=Title("Handling when unhealthy"),
                                    prefill=DefaultValue("crit"),
                                    elements=[
                                        SingleChoiceElement(name="ignore", title=Title("Ignore")),
                                        SingleChoiceElement(name="ok", title=Title("OK")),
                                        SingleChoiceElement(name="warn", title=Title("WARN")),
                                        SingleChoiceElement(name="crit", title=Title("CRIT")),
                                    ],
                                ),
                            ),
                        },
                    ),
                ),
            ),
        },
        ignored_elements=("percent_ssd_life_left",),
    )


rule_spec_rubrik_node_hardware_status = CheckParameters(
    name="rubrik_node_hardware_status",
    title=Title("Rubrik Node Hardware Health"),
    topic=Topic.STORAGE,
    condition=HostCondition(),
    parameter_form=_parameter_form,
)
