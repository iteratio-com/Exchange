from cmk.rulesets.v1 import Help, Title
from cmk.rulesets.v1.form_specs import (
    DataSize,
    DefaultValue,
    DictElement,
    Dictionary,
    IECMagnitude,
    InputHint,
    Integer,
    LevelDirection,
    Percentage,
    ServiceState,
    SimpleLevels,
    TimeMagnitude,
    TimeSpan,
    migrate_to_float_simple_levels,
    migrate_to_integer_simple_levels,
)
from cmk.rulesets.v1.rule_specs import CheckParameters, HostAndItemCondition, Topic


def formspec_maxdb_sessions() -> Dictionary:
    return Dictionary(
        elements={
            "levels_abs": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Absolut levels on active sessions"),
                    migrate=migrate_to_integer_simple_levels,
                    form_spec_template=Integer(),
                    level_direction=LevelDirection.UPPER,
                    prefill_fixed_levels=InputHint((0, 0)),
                ),
            ),
            "levels_perc": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Session Usage Levels"),
                    help_text=Help(
                        "Set here your limits on Sessions Usage (from Max User Sessions)"
                    ),
                    migrate=migrate_to_float_simple_levels,
                    form_spec_template=Percentage(),
                    level_direction=LevelDirection.UPPER,
                    prefill_fixed_levels=DefaultValue((80.0, 90.0)),
                ),
            ),
        }
    )


rule_spec_maxdb_sessions = CheckParameters(
    name="maxdb_sessions",
    topic=Topic.APPLICATIONS,
    parameter_form=formspec_maxdb_sessions,
    title=Title("SAP-MaxDB Sessions"),
    condition=HostAndItemCondition(item_title=Title("Database")),
)

MAGNITUDES = tuple(IECMagnitude)[:4]
MAX_DB_SIZE_ELEMENTS = {
    "levels_perc": DictElement(
        parameter_form=SimpleLevels(
            title=Title("Usage Levels"),
            help_text=Help("Set the utilization thresholds here"),
            migrate=migrate_to_float_simple_levels,
            form_spec_template=Percentage(),
            level_direction=LevelDirection.UPPER,
            prefill_fixed_levels=DefaultValue((80.0, 90.0)),
        ),
    ),
    "levels_bytes": DictElement(
        parameter_form=SimpleLevels(
            title=Title("Size Levels"),
            form_spec_template=DataSize(displayed_magnitudes=MAGNITUDES),
            level_direction=LevelDirection.UPPER,
            migrate=migrate_to_float_simple_levels,
            prefill_fixed_levels=InputHint((0, 0)),
        ),
    ),
}


def _parameter_formspec_maxdb_log() -> Dictionary:
    return Dictionary(elements=MAX_DB_SIZE_ELEMENTS)


rule_spec_maxdb_db_sizes_log = CheckParameters(
    name="maxdb_db_sizes_log",
    topic=Topic.APPLICATIONS,
    parameter_form=_parameter_formspec_maxdb_log,
    title=Title("SAP-MaxDB LOG Sizes"),
    condition=HostAndItemCondition(item_title=Title("DataBase")),
)


def _parameter_formspec_maxdb_db_sizes() -> Dictionary:
    return Dictionary(
        elements={
            **MAX_DB_SIZE_ELEMENTS,
            "badindexes": DictElement(
                parameter_form=ServiceState(
                    title=Title("Set here the Status for bad indexes"),
                    help_text=Help(
                        "Set the criticality here for a number of bad indexes greater than zero"
                    ),
                    prefill=DefaultValue(ServiceState.WARN),
                )
            ),
            "badvolumes": DictElement(
                parameter_form=ServiceState(
                    title=Title("Set here the Status for bad volumes"),
                    help_text=Help(
                        "Set the criticality here for a number of bad volumes greater than zero"
                    ),
                    prefill=DefaultValue(ServiceState.CRIT),
                )
            ),
        }
    )


rule_spec_maxdb_db_sizes = CheckParameters(
    name="maxdb_db_sizes",
    topic=Topic.APPLICATIONS,
    parameter_form=_parameter_formspec_maxdb_db_sizes,
    title=Title("SAP-MaxDB Database Sizes"),
    condition=HostAndItemCondition(item_title=Title("DataBase")),
)


def _parameter_formspec_maxdb_db_config() -> Dictionary:
    return Dictionary(
        elements={
            "autosave": DictElement(
                required=True,
                parameter_form=ServiceState(
                    title=Title("Set here the Status for AutoSave OFF"),
                    help_text=Help(
                        "The AutoSave options is importand for some usechases. "
                        "If this Option is not 'ON' the criticality can set here."
                    ),
                    prefill=DefaultValue(ServiceState.OK),
                ),
            )
        }
    )


rule_spec_maxdb_db_config = CheckParameters(
    name="maxdb_db_config",
    topic=Topic.APPLICATIONS,
    parameter_form=_parameter_formspec_maxdb_db_config,
    title=Title("SAP-MaxDB Database Settings"),
    condition=HostAndItemCondition(item_title=Title("DataBase")),
)


def _parameter_formspec_maxdb_backups() -> Dictionary:
    return Dictionary(
        elements={
            "age_log": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Age of LOG_* Backup Jobs"),
                    help_text=Help("Specify the threshold values for the last backup here"),
                    migrate=migrate_to_float_simple_levels,
                    form_spec_template=TimeSpan(
                        displayed_magnitudes=[
                            TimeMagnitude.DAY,
                            TimeMagnitude.HOUR,
                            TimeMagnitude.MINUTE,
                        ]
                    ),
                    level_direction=LevelDirection.UPPER,
                    prefill_fixed_levels=InputHint((0, 0)),
                ),
            ),
            "age_data": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Age of DAT_* Backup Jobs"),
                    help_text=Help("Specify the threshold values for the last backup here"),
                    migrate=migrate_to_float_simple_levels,
                    form_spec_template=TimeSpan(
                        displayed_magnitudes=[
                            TimeMagnitude.DAY,
                            TimeMagnitude.HOUR,
                            TimeMagnitude.MINUTE,
                        ]
                    ),
                    level_direction=LevelDirection.UPPER,
                    prefill_fixed_levels=InputHint((0, 0)),
                ),
            ),
        }
    )


rule_spec_maxdb_backups = CheckParameters(
    name="maxdb_backups",
    topic=Topic.APPLICATIONS,
    parameter_form=_parameter_formspec_maxdb_backups,
    title=Title("SAP-MaxDB Backup"),
    condition=HostAndItemCondition(item_title=Title("DataBase")),
)
