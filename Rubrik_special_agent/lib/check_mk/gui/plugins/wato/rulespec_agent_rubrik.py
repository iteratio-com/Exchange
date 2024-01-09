#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# 2023, marcus.klein@iteratio.com

from cmk.gui.i18n import _
from cmk.gui.plugins.wato.special_agents.common import RulespecGroupDatasourceProgramsApps
from cmk.gui.plugins.wato.utils import HostRulespec, IndividualOrStoredPassword, rulespec_registry
from cmk.gui.valuespec import Checkbox, Dictionary, TextInput, DualListChoice
from cmk.gui.watolib.rulespecs import Rulespec


def _factory_default_special_agents_rubrik():
    # No default, do not use setting if no rule matches
    return Rulespec.FACTORY_DEFAULT_UNUSED


def _valuespec_special_agents_rubrik():
    return Dictionary(
        title=_("Rubrik Special Agent"),
        help=_("This rule is used to set up Rubrik Special agent."),
        elements=[
            (
                "user",
                TextInput(title=_("User"), allow_empty=False),
            ),
            ("secret", IndividualOrStoredPassword(title=_("Secret of API user"))),
            (
                "verify_ssl",
                Checkbox(
                    title=_("Enable SSL certificate verification"),
                    label=_("Enable verification"),
                ),
            ),
            (
                "sections",
                DualListChoice(
                    title=_("Sections"),
                    choices=[
                        ("cluster_system_status", _("Rubrik Cluster System Status")),
                        (
                            "cluster_compliance_status",
                            _("Rubrik Cluster Report Compliance Status 24h"),
                        ),
                        ("node_status", _("Rubrik Node Status")),
                        ("node_disk_status", _("Rubrik Node Disk Status")),
                        ("node_hardware_health", _("Rubrik Node Hardware Health")),
                    ],
                    help=_("Select the sections to be monitored, default are all sections."),
                    rows=7,
                ),
            ),
        ],
        required_keys=["user", "secret", "verify_ssl"],
    )


rulespec_registry.register(
    HostRulespec(
        factory_default=_factory_default_special_agents_rubrik(),
        group=RulespecGroupDatasourceProgramsApps,
        name="special_agents:rubrik",
        valuespec=_valuespec_special_agents_rubrik,
    )
)
