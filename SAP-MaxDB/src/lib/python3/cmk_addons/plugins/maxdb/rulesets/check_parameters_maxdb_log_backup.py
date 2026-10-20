from cmk.rulesets.v1 import Title
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    LevelDirection,
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


def form() -> Dictionary:
    return Dictionary(
        elements={
            "age": DictElement(parameter_form=levels_time("Log backup age", 86400.0, 172800.0)),
            "failed_state": DictElement(
                parameter_form=ServiceState(
                    title=Title("Latest backup attempt failed"),
                    prefill=DefaultValue(ServiceState.WARN),
                ),
            ),
            "auto_log_off": DictElement(
                parameter_form=ServiceState(
                    title=Title("Automatic log backup OFF"), prefill=DefaultValue(ServiceState.WARN)
                ),
            ),
        }
    )


rule_spec_maxdb_log_backup = CheckParameters(
    name="maxdb_log_backup",
    topic=Topic.APPLICATIONS,
    parameter_form=form,
    title=Title("MaxDB Log Backup"),
    condition=HostAndItemCondition(item_title=Title("Database")),
)
