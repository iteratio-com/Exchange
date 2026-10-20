from cmk.rulesets.v1 import Title
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    Integer,
    LevelDirection,
    ServiceState,
    SimpleLevels,
    migrate_to_integer_simple_levels,
)
from cmk.rulesets.v1.rule_specs import CheckParameters, HostAndItemCondition, Topic


def levels(title: str, warn: int, crit: int) -> SimpleLevels:
    return SimpleLevels(
        title=Title(title),
        form_spec_template=Integer(),
        level_direction=LevelDirection.UPPER,
        migrate=migrate_to_integer_simple_levels,
        prefill_fixed_levels=DefaultValue((warn, crit)),
    )


def form() -> Dictionary:
    return Dictionary(
        elements={
            "lock_usage": DictElement(
                required=False, parameter_form=levels("Lock usage (%)", 80, 90)
            ),
            "waiting": DictElement(required=False, parameter_form=levels("Waiting requests", 1, 5)),
        }
    )


rule_spec_maxdb_locks = CheckParameters(
    name="maxdb_locks",
    topic=Topic.APPLICATIONS,
    parameter_form=form,
    title=Title("MaxDB Locks"),
    condition=HostAndItemCondition(item_title=Title("Database")),
)
