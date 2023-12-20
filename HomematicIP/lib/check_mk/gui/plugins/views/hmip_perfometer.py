#!/usr/bin/env python3

from cmk.gui.plugins.metrics.utils import perfometer_info

perfometer_info.append(
    {
        "type": "dual",
        "perfometers": [
            {
                "type": "linear",
                "segments": ["valveactualtemperature"],
                "total": 35.0,
            },
            {
                "type": "linear",
                "segments": ["setpointtemperature"],
                "total": 35.0,
            },
        ],
    }
)
