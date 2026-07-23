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
    Alternative,
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
                                "auth",
                                Alternative(
                                    title=_("Authentication"),
                                    help=_(
                                        "Choose how the plugin authenticates against the MaxDB. "
                                        "Using an XUSER key (dbmcli -U &lt;key&gt;) is recommended, "
                                        "as it avoids storing the password in clear text in the "
                                        "agent configuration file maxdb.cfg. The XUSER key must be "
                                        "created beforehand with <tt>xuser set</tt> for the OS user "
                                        "that runs the Checkmk agent."
                                    ),
                                    elements=[
                                        Dictionary(
                                            title=_("XUSER key (no plaintext password)"),
                                            elements=[
                                                (
                                                    "xuser_key",
                                                    TextInput(
                                                        title=_("XUSER key"),
                                                        regex="^[A-Za-z0-9_.-]+$",
                                                        regex_error=_(
                                                            "Only letters, digits and _.- are allowed."
                                                        ),
                                                        help=_(
                                                            "Name of the XUSER entry to use with "
                                                            "dbmcli -U. Create it with e.g. "
                                                            "<tt>xuser set -U MONCSP -d CSP -u "
                                                            "MONITOR,secret</tt> as the agent's OS user."
                                                        ),
                                                        allow_empty=False,
                                                    ),
                                                ),
                                            ],
                                            optional_keys=[],
                                        ),
                                        Dictionary(
                                            title=_("User and password (clear text in maxdb.cfg)"),
                                            elements=[
                                                (
                                                    "user",
                                                    TextInput(
                                                        title=_("Username"),
                                                        help=_("User for Login into the MaxDB"),
                                                    ),
                                                ),
                                                (
                                                    "password",
                                                    Password(
                                                        title=_("Password of User"),
                                                        help=_(
                                                            "Password for the user. Be careful the "
                                                            "password is in clear text in the agent "
                                                            "configuration."
                                                        ),
                                                    ),
                                                ),
                                            ],
                                            optional_keys=[],
                                        ),
                                    ],
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
