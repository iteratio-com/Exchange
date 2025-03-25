#!/usr/bin/env python3


from cmk.gui.i18n import _
from cmk.gui.plugins.wato.utils import HostRulespec, rulespec_registry
from cmk.gui.cee.agent_bakery import RulespecGroupMonitoringAgentsAgentPlugins
from cmk.gui.valuespec import Age, Alternative, Dictionary, FixedValue


def _valuespec_agent_config_windows_fsrm():
    return Alternative(
        title=_("Windows File Server Ressource Manager (FSRM)"),
        help=_("With this Rule the Powershell Plugin for FSRM gets deployed."),
        elements=[
            Dictionary(
                title=_("Deploy the fsrm quota plug-in"),
                elements=[
                    (
                        "interval",
                        Age(
                            title=_("Run asynchronously"),
                            label=_("Interval for collecting data"),
                            default_value=300,
                        ),
                    ),
                ],
            ),
            FixedValue(
                value=None,
                title=_("Do not deploy the fsrm quota plug-in"),
                totext=_("(disabled)"),
            ),
        ],
    )


rulespec_registry.register(
    HostRulespec(
        group=RulespecGroupMonitoringAgentsAgentPlugins,
        name="agent_config:windows_fsrm",
        valuespec=_valuespec_agent_config_windows_fsrm,
    )
)
