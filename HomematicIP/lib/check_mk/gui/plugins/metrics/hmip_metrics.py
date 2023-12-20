#!/usr/bin/env python3

from cmk.gui.i18n import _
from cmk.gui.plugins.metrics.utils import graph_info, metric_info

metric_info["valveposition"] = {
    "title": _("Valve position"),
    "unit": "%",
    "color": "15/a",
}

metric_info["rssi"] = {
    "title": _("RSSI Value"),
    "unit": "count",
    "color": "#1393BA",
}

metric_info["setpointtemperature"] = {
    "title": _("Setpoint temperature"),
    "unit": "c",
    "color": "#BAB413",
}

metric_info["valveactualtemperature"] = {
    "title": _("Valve actual temperature"),
    "unit": "c",
    "color": "#E81022",
}

graph_info["hmip_heatingthermostat"] = {
    "title": _("Temperatures Thermostat"),
    "metrics": [
        ("setpointtemperature", "area"),
        ("valveactualtemperature", "area"),
    ],
}
