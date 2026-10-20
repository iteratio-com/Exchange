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


def form() -> Dictionary:
    return Dictionary(
        elements={
            "age": DictElement(
                required=False,
                parameter_form=SimpleLevels(
                    title=Title("Data backup age"),
                    form_spec_template=TimeSpan(
                        displayed_magnitudes=[
                            TimeMagnitude.DAY,
                            TimeMagnitude.HOUR,
                            TimeMagnitude.MINUTE,
                            TimeMagnitude.SECOND,
                        ]
                    ),
                    level_direction=LevelDirection.UPPER,
                    prefill_fixed_levels=DefaultValue((172800.0, 259200.0)),
                ),
            ),
            "failed_state": DictElement(
                parameter_form=ServiceState(
                    title=Title("Latest backup attempt failed"),
                    prefill=DefaultValue(ServiceState.WARN),
                ),
            ),
        }
    )


rule_spec_maxdb_data_backup = CheckParameters(
    name="maxdb_data_backup",
    topic=Topic.APPLICATIONS,
    parameter_form=form,
    title=Title("MaxDB Data Backup"),
    condition=HostAndItemCondition(item_title=Title("Database")),
)
