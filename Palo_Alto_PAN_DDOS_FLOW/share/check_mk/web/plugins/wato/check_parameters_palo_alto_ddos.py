#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cmk.gui.i18n import _
from cmk.gui.plugins.wato.utils import (
    CheckParameterRulespecWithoutItem,
    rulespec_registry,
    RulespecGroupCheckParametersApplications,
)
from cmk.gui.valuespec import Dictionary, Float, Tuple

default_tuple = [Float(title=_("Warning at")), Float(title=_("Critical at"))]


def _parameter_valuespec_palo_alto_ddos():
    return Dictionary(elements=[
        ("policy_deny", Tuple(title=_("Levels on Sessions denied by policy"),
                              elements=default_tuple)),
        ("flow_dos_rule_drop",
         Tuple(title=_("Levels on Packets dropped by Rate limited or IP blocked"),
               elements=default_tuple)),
        ("dos_drop_ip_blocked",
         Tuple(title=_(
             "Levels on Packets dropped by Flagged for blocking and under block duration by other"),
               elements=default_tuple)),
        ("dos_blk_sw_entries",
         Tuple(title=_("Levels on DOS Software block table"), elements=default_tuple)),
        ("dos_blk_hw_entries",
         Tuple(title=_("Levels on DOS Hardware block table"), elements=default_tuple)),
        ("dos_blk_num_entries",
         Tuple(title=_("Levels on DOS block table Entries"), elements=default_tuple)),
    ],
                      optional_keys=[
                          "policy_deny", "flow_dos_rule_drop", "dos_drop_ip_blocked",
                          "dos_blk_sw_entries", "dos_blk_hw_entries", "dos_blk_num_entries"
                      ])


rulespec_registry.register(
    CheckParameterRulespecWithoutItem(
        check_group_name="palo_alto_ddos",
        group=RulespecGroupCheckParametersApplications,
        parameter_valuespec=_parameter_valuespec_palo_alto_ddos,
        title=lambda: _("Palo Alto: PAN Zone/DoS Protection"),
    ))
