#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cmk.gui.i18n import _
from cmk.gui.plugins.metrics import metric_info, graph_info

metric_info["datacache_hitrate"] = {
    "title": _("Datacache Hitrate"),
    "unit": "%",
    "color": "15/a",
}

metric_info["session_usage"] = {
    "title": _("Session Usage"),
    "unit": "%",
    "color": "15/a",
}

metric_info["last_data_job"] = {
    "title": _("Last Data Backup Job"),
    "unit": "s",
    "color": "45/a",
}

metric_info["last_log_job"] = {
    "title": _("Last Log Backup Job"),
    "unit": "s",
    "color": "35/a",
}
## Data

metric_info["database_usage_perc"] = {
    "title": _("Database Usage"),
    "unit": "%",
    "color": "15/a",
}

metric_info["usable_size_bytes"] = {
    "title": _("Total Size"),
    "unit": "bytes",
    "color": "15/a",
}
metric_info["used_size_bytes"] = {
    "title": _("Used Size"),
    "unit": "bytes",
    "color": "25/a",
}

graph_info["maxdbdatabaseusagebytes"] = {
    "title": _("Database Usage"),
    "metrics": [
        ("used_size_bytes", "area"),
        ("usable_size_bytes", "line"),
    ],
}

## LOG

metric_info["used_log_pages_perc"] = {
    "title": _("Log Pages Usage"),
    "unit": "%",
    "color": "15/a",
}

metric_info["used_log_pages_bytes"] = {
    "title": _("Used Log Pages"),
    "unit": "bytes",
    "color": "25/a",
}
metric_info["log_pages_bytes"] = {
    "title": _("Total Aviable LOG Pages"),
    "unit": "bytes",
    "color": "15/a",
}

metric_info["used_log_pages"] = {
    "title": _("Used Log Pages"),
    "unit": "count",
    "color": "25/a",
}
metric_info["log_pages"] = {
    "title": _("Total Aviable Log Pages"),
    "unit": "count",
    "color": "15/a",
}

graph_info["maxdblogbytes"] = {
    "title": _("Log Pages (Size)"),
    "metrics": [
        ("used_log_pages_bytes", "area"),
        ("log_pages_bytes", "line"),
    ],
}

graph_info["maxdblogpages"] = {
    "title": _("Log Pages (Pages)"),
    "metrics": [
        ("used_log_pages", "area"),
        ("log_pages", "line"),
    ],
}
