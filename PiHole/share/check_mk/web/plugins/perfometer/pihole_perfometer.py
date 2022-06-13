#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

from cmk.gui.plugins.metrics import perfometer_info

perfometer_info.append({
    "type": "logarithmic",
    "metric": "ads_percentage_today",
    "half_value": 50,
    "exponent": 2.0,
})

perfometer_info.append({
    "type": "logarithmic",
    "metric": "db_file_size",
    "half_value": 1726758912,
    "exponent": 2.0,
})

perfometer_info.append({
    "type": "logarithmic",
    "metric": "gravity_last_updated",
    "half_value": 172800,
    "exponent": 2.0,
})

perfometer_info.append({
    "type": "logarithmic",
    "metric": "total_messages",
    "half_value": 10,
    "exponent": 2.0,
})

perfometer_info.append({
    "type":
    "stacked",
    "perfometers": [
        {
            "type": "logarithmic",
            "metric": "ads_over_time_10min",
            "half_value": 1000,
            "exponent": 2,
        },
        {
            "type": "logarithmic",
            "metric": "domains_over_time_10min",
            "half_value": 1000,
            "exponent": 2,
        },
    ],
})
