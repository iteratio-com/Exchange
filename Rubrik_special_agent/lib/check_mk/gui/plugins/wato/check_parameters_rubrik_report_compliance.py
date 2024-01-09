#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# 2023, marcus.klein@iteratio.com

from cmk.gui.i18n import _

from cmk.gui.plugins.wato.utils import (
    CheckParameterRulespecWithoutItem,
    RulespecGroupCheckParametersApplications,
    rulespec_registry,
)
from cmk.gui.valuespec import Dictionary, Integer, Tuple


def _parameter_valuespec_rubrik_cluster_compliance_24_hours() -> Dictionary:
    return Dictionary(
        elements=[
            (
                "absolute_out_of_compliance",
                Tuple(
                    title="Absolute levels for snapshots out of compliance",
                    elements=[
                        Integer(
                            title=_("Warning if more or equal than"), default_value=1
                        ),
                        Integer(
                            title=_("Critical if more or equal than"), default_value=5
                        ),
                    ],
                ),
            ),
            (
                "percent_out_of_compliance",
                Tuple(
                    title="Percentage levels for snapshots out of compliance",
                    elements=[
                        Integer(
                            title=_("Warning if mor or equal than"),
                            default_value=1,
                            unit="%",
                        ),
                        Integer(
                            title=_("Critical if more or equal than"),
                            default_value=5,
                            unit="%",
                        ),
                    ],
                ),
            ),
        ],
    )


rulespec_registry.register(
    CheckParameterRulespecWithoutItem(
        check_group_name="rubrik_cluster_compliance_24_hours",
        group=RulespecGroupCheckParametersApplications,
        parameter_valuespec=_parameter_valuespec_rubrik_cluster_compliance_24_hours,
        title=lambda: _("Rubrik Compliance 24 Hours Snapshot Levels"),
    )
)
