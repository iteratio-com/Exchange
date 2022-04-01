#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cmk.gui.i18n import _
from cmk.gui.plugins.wato.utils import (CheckParameterRulespecWithoutItem, rulespec_registry,
                                        RulespecGroupCheckParametersEnvironment)
from cmk.gui.valuespec import (Dictionary, Age, Tuple)


def _parameter_valuespec_snmp_systemtime():
    return Dictionary(
        elements=[
            ("levels",
             Tuple(title=_("Time offset boundaries"),
                   help=_("This are the allowed time offsets"),
                   elements=[
                       Age(title=_("Warning at"), default_value=100, display=["minutes",
                                                                              "seconds"]),
                       Age(title=_("Critical at"),
                           default_value=180,
                           display=["minutes", "seconds"]),
                   ])),
        ],
        optional_keys=[],
    )


rulespec_registry.register(
    CheckParameterRulespecWithoutItem(
        check_group_name="snmp_systemtime_group",
        group=RulespecGroupCheckParametersEnvironment,
        match_type="dict",
        parameter_valuespec=_parameter_valuespec_snmp_systemtime,
        title=lambda: _("SNMP system time offset"),
    ))
