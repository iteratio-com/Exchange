from cmk.rulesets.v1 import Title
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    Integer,
    LevelDirection,
    Percentage,
    ServiceState,
    SimpleLevels,
    TimeMagnitude,
    TimeSpan,
)
from cmk.rulesets.v1.rule_specs import CheckParameters, HostAndItemCondition, Topic


def levels_time(title: str, warn: float, crit: float) -> SimpleLevels:
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


def levels_percent(title: str, warn: float, crit: float) -> SimpleLevels:
    return SimpleLevels(
        title=Title(title),
        form_spec_template=Percentage(),
        level_direction=LevelDirection.UPPER,
        prefill_fixed_levels=DefaultValue((warn, crit)),
    )


def levels(title: str, warn: int, crit: int) -> SimpleLevels:
    return SimpleLevels(
        title=Title(title),
        form_spec_template=Integer(),
        level_direction=LevelDirection.UPPER,
        prefill_fixed_levels=DefaultValue((warn, crit)),
    )


def form() -> Dictionary:
    return Dictionary(
        elements={
            "lock_usage": DictElement(parameter_form=levels_percent("Lock usage (%)", 80.0, 90.0)),
            "waiting": DictElement(parameter_form=levels("Waiting requests", 1, 5)),
            "usage": DictElement(
                parameter_form=levels_percent("Data volume usage (%)", 80.0, 90.0)
            ),
            "age": DictElement(
                parameter_form=levels_time("Transaction age", 900.0, 3600.0),
            ),
            "data_age": DictElement(
                parameter_form=levels_time("Data backup age", 172800.0, 259200.0),
            ),
            "log_age": DictElement(
                parameter_form=levels_time("Log backup age", 86400.0, 172800.0),
            ),
            "auto_log_off": DictElement(
                parameter_form=ServiceState(
                    title=Title("Automatic log backup OFF"),
                    prefill=DefaultValue(ServiceState.WARN),
                ),
            ),
        }
    )


rule_spec_maxdb_extended = CheckParameters(
    name="maxdb_extended",
    topic=Topic.APPLICATIONS,
    parameter_form=form,
    title=Title("MaxDB extended monitoring (legacy; migrate rules manually)"),
    condition=HostAndItemCondition(item_title=Title("Database")),
)
