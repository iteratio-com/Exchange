#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cmk.gui.plugins.metrics import perfometer_info

perfometer_info.append({
    "type": "linear",
    "segments": ["used_log_pages_perc"],
    "total": 100.0,
})

perfometer_info.append({
    "type": "linear",
    "segments": ["database_usage_perc"],
    "total": 100.0,
})

perfometer_info.append({
    "type": "linear",
    "segments": ["datacache_hitrate"],
    "total": 100.0,
})

perfometer_info.insert(
    0,
    {
        "type": "linear",
        "segments": ["session_usage"],
        "total": 100.0,
    },
)
