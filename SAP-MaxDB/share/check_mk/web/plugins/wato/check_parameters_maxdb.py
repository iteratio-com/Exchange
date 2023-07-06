#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cmk.gui.i18n import _
from cmk.gui.plugins.wato.utils import (
    CheckParameterRulespecWithItem,
    rulespec_registry,
    RulespecGroupCheckParametersEnvironment,
)
from cmk.gui.valuespec import (
    Dictionary,
    Integer,
    TextInput,
    Percentage,
    Tuple,
    Filesize,
    MonitoringState,
    Age,
)


def _parameter_valuespec_maxdb_sessions():
    return Dictionary(
        elements=[
            (
                "levels_abs",
                Tuple(
                    title=_("Absolut levels on active sessions"),
                    help=_(
                        "Specify the threshold values for the absolute number of active sessions here"
                    ),
                    elements=[
                        Integer(
                            title=_("Warning at"),
                        ),
                        Integer(
                            title=_("Critical at"),
                        ),
                    ],
                ),
            ),
            (
                "levels_perc",
                Tuple(
                    title=_("Session Usage Levels"),
                    help=_(
                        "Set here your limits on Sessions Usage (from Max User Sessions)"
                    ),
                    elements=[
                        Percentage(title=_("Warning at"), default_value=80),
                        Percentage(title=_("Critical at"), default_value=90),
                    ],
                ),
            ),
        ],
        optional_keys=["levels_abs", "levels_perc"],
    )


rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name="maxdb_sessions",
        group=RulespecGroupCheckParametersEnvironment,
        item_spec=lambda: TextInput(
            title=_("Database"), help=_("Name of the Database")
        ),
        match_type="dict",
        parameter_valuespec=_parameter_valuespec_maxdb_sessions,
        title=lambda: _("SAP-MaxDB Sessions"),
    )
)

max_db_size_elements = [
    (
        "levels_perc",
        Tuple(
            title=_("Usage Levels"),
            help=_("Set the utilization thresholds here"),
            elements=[
                Percentage(title=_("Warning at"), default_value=80),
                Percentage(title=_("Critical at"), default_value=90),
            ],
        ),
    ),
    (
        "levels_bytes",
        Tuple(
            title=_("Size Levels"),
            help=_("Specify the threshold values for absolute utilization here"),
            elements=[
                Filesize(title=_("Warning at")),
                Filesize(title=_("Critical at")),
            ],
        ),
    ),
]


def _parameter_valuespec_maxdb_log():
    return Dictionary(
        elements=max_db_size_elements,
        optional_keys=["levels_bytes", "levels_perc"],
    )


rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name="maxdb_db_sizes_log",
        group=RulespecGroupCheckParametersEnvironment,
        item_spec=lambda: TextInput(
            title=_("DataBase"), help=_("Name of the Database")
        ),
        match_type="dict",
        parameter_valuespec=_parameter_valuespec_maxdb_log,
        title=lambda: _("SAP-MaxDB LOG Sizes"),
    )
)

rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name="maxdb_db_sizes_log",
        group=RulespecGroupCheckParametersEnvironment,
        item_spec=lambda: TextInput(
            title=_("DataBase"), help=_("Name of the Database")
        ),
        match_type="dict",
        parameter_valuespec=_parameter_valuespec_maxdb_log,
        title=lambda: _("SAP-MaxDB LOG Sizes"),
    )
)


def _parameter_valuespec_maxdb_database():
    return Dictionary(
        elements=max_db_size_elements
        + [
            (
                "badindexes",
                MonitoringState(
                    title=_("Set here the Status for bad indexes"),
                    help=_(
                        "Set the criticality here for a number of bad indexes greater than zero"
                    ),
                    default_value=1,
                ),
            ),
            (
                "badvolumes",
                MonitoringState(
                    title=_("Set here the Status for bad volumes"),
                    help=_(
                        "Set the criticality here for a number of bad volumes greater than zero"
                    ),
                    default_value=2,
                ),
            ),
        ],
        optional_keys=["levels_bytes", "levels_perc", "badindexes", "badvolumes"],
    )


rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name="maxdb_db_sizes",
        group=RulespecGroupCheckParametersEnvironment,
        item_spec=lambda: TextInput(
            title=_("DataBase"), help=_("Name of the Database")
        ),
        match_type="dict",
        parameter_valuespec=_parameter_valuespec_maxdb_database,
        title=lambda: _("SAP-MaxDB Database Sizes"),
    )
)


def _parameter_valuespec_maxdb_settings():
    return Dictionary(
        elements=[
            (
                "autosave",
                MonitoringState(
                    title=_("Set here the Status for AutoSave OFF"),
                    help=_(
                        "The AutoSave options is importand for some usechases. If this Option is not 'ON' the criticality can set here."
                    ),
                    default_value=0,
                ),
            ),
        ],
        optional_keys=[],
    )


rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name="maxdb_db_config",
        group=RulespecGroupCheckParametersEnvironment,
        item_spec=lambda: TextInput(
            title=_("DataBase"), help=_("Name of the Database")
        ),
        match_type="dict",
        parameter_valuespec=_parameter_valuespec_maxdb_settings,
        title=lambda: _("SAP-MaxDB Database Settings"),
    )
)


def _parameter_valuespec_maxdb_backup():
    return Dictionary(
        elements=[
            (
                "age_log",
                Tuple(
                    title=_("Age of LOG_* Backup Jobs"),
                    help=_("Specify the threshold values for the last backup here"),
                    elements=[
                        Age(title=_("Warning at")),
                        Age(title=_("Critical at")),
                    ],
                ),
            ),
            (
                "age_data",
                Tuple(
                    title=_("Age of DAT_* Backup Jobs"),
                    help=_("Specify the threshold values for the last backup here"),
                    elements=[
                        Age(title=_("Warning at")),
                        Age(title=_("Critical at")),
                    ],
                ),
            ),
        ],
        optional_keys=["age_log", "age_data"],
    )


rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name="maxdb_backups",
        group=RulespecGroupCheckParametersEnvironment,
        item_spec=lambda: TextInput(
            title=_("DataBase"), help=_("Name of the Database")
        ),
        match_type="dict",
        parameter_valuespec=_parameter_valuespec_maxdb_backup,
        title=lambda: _("SAP-MaxDB Backup"),
    )
)
