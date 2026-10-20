from cmk.rulesets.v1 import Title
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    Float,
    LevelDirection,
    SimpleLevels,
)
from cmk.rulesets.v1.rule_specs import CheckParameters, HostAndItemCondition, Topic


def levels(title: str, warn: float, crit: float) -> SimpleLevels:
    return SimpleLevels(
        title=Title(title),
        form_spec_template=Float(unit_symbol="/s"),
        level_direction=LevelDirection.UPPER,
        prefill_fixed_levels=DefaultValue((warn, crit)),
    )


def form() -> Dictionary:
    return Dictionary(
        elements={
            "waits_rate": DictElement(parameter_form=levels("SQL waits per second", 10.0, 50.0)),
            "physical_reads_rate": DictElement(
                parameter_form=levels("SQL physical reads per second", 100.0, 500.0)
            ),
        }
    )


rule_spec_maxdb_performance = CheckParameters(
    name="maxdb_performance",
    topic=Topic.APPLICATIONS,
    parameter_form=form,
    title=Title("MaxDB SQL Performance"),
    condition=HostAndItemCondition(item_title=Title("Database")),
)
