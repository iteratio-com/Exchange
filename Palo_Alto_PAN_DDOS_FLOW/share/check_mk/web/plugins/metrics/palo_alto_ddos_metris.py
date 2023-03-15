#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

from cmk.gui.i18n import _
from cmk.gui.plugins.metrics import metric_info


info = (
    ('DOS Hardware block table', 'dos_blk_hw_entries', "11/a"), 
    ('DOS block table Entries','dos_blk_num_entries', "21/a"),
    ('DOS Software block table', 'dos_blk_sw_entries', "31/a"), 
    ('Packets dropped by Flagged for blocking and under block duration by other', 'dos_drop_ip_blocked', "25/a"),
    ('Packets dropped by Rate limited or IP blocked', 'flow_dos_rule_drop', "11/b"), 
    ('Session denied by policy', 'policy_deny', "23/a")
)

for i,j,c in info:
    metric_info[j]={
        "title":_(i),
        "unit": "count",
        "color": c
    }