#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cmk.gui.i18n import _
from cmk.gui.valuespec import (
    DropdownChoice,
)
from cmk.gui.plugins.wato import (
    HostRulespec,
    rulespec_registry,
)

try:
    from cmk.gui.cee.plugins.wato.agent_bakery.rulespecs.utils import (
        RulespecGroupMonitoringAgentsAgentPlugins,
    )
except Exception:
    RulespecGroupMonitoringAgentsAgentPlugins = None


def _valuespec_agent_config_wsus_next_reboot():
    return DropdownChoice(
        title=_("WSUS next reboot Plugin"),
        help=_(
            "This will deploy the agent plugin <tt>wsus_next_reboot.ps1</tt> on windows systems."
        ),
        choices=[
            (True, _("Deploy WSUS next reboot plugin")),
            (None, _("Do not deploy WSUS next reboot plugin")),
        ],
    )


if RulespecGroupMonitoringAgentsAgentPlugins is not None:
    rulespec_registry.register(
        HostRulespec(
            group=RulespecGroupMonitoringAgentsAgentPlugins,
            name="agent_config:wsus_next_reboot",
            valuespec=_valuespec_agent_config_wsus_next_reboot,
        )
    )
