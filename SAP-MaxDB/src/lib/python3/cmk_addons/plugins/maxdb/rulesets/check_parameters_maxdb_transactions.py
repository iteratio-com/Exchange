from cmk.rulesets.v1 import Title
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    LevelDirection,
    SimpleLevels,
    TimeMagnitude,
    TimeSpan,
)
from cmk.rulesets.v1.rule_specs import CheckParameters, HostAndItemCondition, Topic


def levels(title: str, warn: float, crit: float) -> SimpleLevels:
    return SimpleLevels(
        title=Title(title),
        form_spec_template=TimeSpan(
            displayed_magnitudes=[
                TimeMagnitude.DAY,
                TimeMagnitude.HOUR,
                TimeMagnitude.MINUTE,
                TimeMagnitude.SECOND,
            ]
        ),
        level_direction=LevelDirection.UPPER,
        prefill_fixed_levels=DefaultValue((warn, crit)),
    )


def form() -> Dictionary:
    return Dictionary(
        elements={
            "age": DictElement(
                required=True, parameter_form=levels("Transaction age (seconds)", 900.0, 3600.0)
            ),
        }
    )


rule_spec_maxdb_transactions = CheckParameters(
    name="maxdb_transactions",
    topic=Topic.APPLICATIONS,
    parameter_form=form,
    title=Title("MaxDB Transactions"),
    condition=HostAndItemCondition(item_title=Title("Database")),
)
