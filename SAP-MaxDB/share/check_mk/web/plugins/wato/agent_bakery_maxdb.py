#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cmk.gui.plugins.wato import (
    rulespec_registry,
    HostRulespec,
)
from cmk.gui.valuespec import (
    Dictionary,
    TextInput,
    ListChoice,
    Integer,
    Password,
    ListOf,
)

from cmk.gui.i18n import _
from cmk.gui.plugins.wato import (
    HostRulespec,
    rulespec_registry,
)
from cmk.gui.cee.plugins.wato.agent_bakery.rulespecs.utils import (
    RulespecGroupMonitoringAgentsAgentPlugins,
)


def _valuespec_agent_config_maxdb():
    return Dictionary(
        elements=[
            (
                "databases",
                ListOf(
                    Dictionary(
                        elements=[
                            (
                                "dbname",
                                TextInput(title=_("Name of Database"), help=_("MaxDB Name")),
                            ),
                            (
                                "user",
                                TextInput(
                                    title=_("Username"), help=_("User for Login into the MaxDB")
                                ),
                            ),
                            (
                                "password",
                                Password(
                                    title=_("Password of User"),
                                    help=_(
                                        "Password for the user. Be careful the password is in clear text in the agent configuration."
                                    ),
                                ),
                            ),
                            (
                                "modules",
                                ListChoice(
                                    title=_("Aviable Modules/Querys to execute"),
                                    help=_(
                                        "The individual queries can be selected here. It is recommended to select State and Data/log usage together."
                                    ),
                                    choices=[
                                        ("state", "Overall State of the DB"),
                                        ("backup:sep(124)", "Backup State"),
                                        ("data:sep(61)", "Data and Log usage"),
                                    ],
                                    columns=1,
                                    toggle_all=True,
                                    default_value=["state", "backup:sep(124)", "data:sep(61)"],
                                ),
                            ),
                            (
                                "cmd_tool",
                                TextInput(
                                    title=_("Path to dbmcli-tool"),
                                    regex="^\/[a-zA-Z_0-9_.-\/]*\/bin\/dbmcli$",
                                    regex_error=_(
                                        "Specify here the full path of dbmcli, starting with <tt>/</tt> and ending with <tt>bin/dbmcli</tt>"
                                    ),
                                    help=_(
                                        "Specify here the full path of the dbmcli, e.g. /sapdb/Databases/db/bin/dbmcli."
                                        " If this Parameter not set it will try to use /sapdb/DBNAME/db/bin/dbmcli"
                                    ),
                                ),
                            ),
                            (
                                "timeout",
                                Integer(
                                    title=_("Execution Timeout for a single Query"),
                                    minvalue=1,
                                    default_value=20,
                                    unit=_("seconds"),
                                ),
                            ),
                        ],
                        optional_keys=["timeout", "cmd_tool"],
                    ),
                    title=_("Specify here the MaxDB/s settings for the Agent Plugin"),
                    add_label=_("Add MaxDB Connection"),
                ),
            ),
            (
                "interval",
                Integer(
                    title=_("Check Interval of the Plugin"),
                    unit=_("seconds"),
                ),
            ),
        ],
        optional_keys=["interval"],
        title=_("Use MaxDB Agent Plugin"),
    )


rulespec_registry.register(
    HostRulespec(
        group=RulespecGroupMonitoringAgentsAgentPlugins,
        name="agent_config:maxdb",
        valuespec=_valuespec_agent_config_maxdb,
    )
)
