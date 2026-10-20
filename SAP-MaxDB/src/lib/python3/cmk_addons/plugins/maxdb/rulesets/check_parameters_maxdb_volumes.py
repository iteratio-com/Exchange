from cmk.rulesets.v1 import Title
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    LevelDirection,
    Percentage,
    SimpleLevels,
)
from cmk.rulesets.v1.rule_specs import CheckParameters, HostAndItemCondition, Topic


def levels(title: str, warn: float, crit: float) -> SimpleLevels:
    return SimpleLevels(
        title=Title(title),
        form_spec_template=Percentage(),
        level_direction=LevelDirection.UPPER,
        prefill_fixed_levels=DefaultValue((warn, crit)),
    )


def form() -> Dictionary:
    return Dictionary(
        elements={
            "usage": DictElement(required=True, parameter_form=levels("Data usage", 80.0, 90.0)),
        }
    )


rule_spec_maxdb_volumes = CheckParameters(
    name="maxdb_volumes",
    topic=Topic.APPLICATIONS,
    parameter_form=form,
    title=Title("MaxDB Data Volumes"),
    condition=HostAndItemCondition(item_title=Title("Database")),
)
