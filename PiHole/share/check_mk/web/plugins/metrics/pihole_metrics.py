#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

from cmk.gui.i18n import _
from cmk.gui.plugins.metrics import metric_info, graph_info

metric_info["ads_over_time_10min"] = {
    "title": _("Ads over the last 10mins"),
    "unit": "count",
    "color": "#cc0000",
}
metric_info["domains_over_time_10min"] = {
    "title": _("Domains over the last 10mins"),
    "unit": "count",
    "color": "#3333ff",
}
graph_info["over_time_10min"] = {
    "title":
    _("Data from the last 10mins"),
    "metrics": [
        ("domains_over_time_10min", "area"),
        ("ads_over_time_10min", "area"),
    ],
}
metric_info["ads_percentage_today"] = {
    "title": _("Ads Percentage Today"),
    "unit": "%",
    "color": "#fff717",
}
metric_info["total_messages"] = {
    "title": _("Total Messages"),
    "unit": "count",
    "color": "#fff717",
}
metric_info["gravity_last_updated"] = {
    "title": _("Gravity Last Updated"),
    "unit": "s",
    "color": "#86eb34",
}
metric_info["db_file_size"] = {
    "title": _("DB File Size"),
    "unit": "bytes",
    "color": "#00dd00",
}
metric_info["clients_ever_seen"] = {
    "title": _("Clients Ever Seen"),
    "unit": "count",
    "color": "#669900",
}
metric_info["domains_being_blocked"] = {
    "title": _("Domains Being Blocked"),
    "unit": "count",
    "color": "#cc0000",
}
metric_info["privacy_level"] = {
    "title": _("Privacy Level"),
    "unit": "count",
    "color": "#00cc00",
}
metric_info["unique_clients"] = {
    "title": _("Unique Clients"),
    "unit": "count",
    "color": "#00cccc",
}

metric_info["unique_domains"] = {
    "title": _("Unique Domains"),
    "unit": "count",
    "color": "#0099cc",
}

metric_info["dns_queries_today"] = {
    "title": _("DNS Queries Today"),
    "unit": "count",
    "color": "#3333ff",
}
metric_info["ads_blocked_today"] = {
    "title": _("Ads Blocked Today"),
    "unit": "count",
    "color": "#cc0000",
}
graph_info["queries_today"] = {
    "title": _("Queries Today"),
    "metrics": [("dns_queries_today", "area"), ("ads_blocked_today", "area")],
}
metric_info["queries_cached"] = {
    "title": _("Queries Cached"),
    "unit": "count",
    "color": "#ffcc00",
}
metric_info["queries_forwarded"] = {
    "title": _("Queries Forwarded"),
    "unit": "count",
    "color": "#cccc00",
}
graph_info["queries_fowarded_cached"] = {
    "title": _("Queries Forwarded/Cached"),
    "metrics": [("queries_forwarded", "area"), ("queries_cached", "area")],
}
metric_info["dns_queries_all_types"] = {
    "title": _("DNS Queries all Types"),
    "unit": "count",
    "color": "#cc0000",
}
metric_info["reply_NODATA"] = {
    "title": _("reply NODATA"),
    "unit": "count",
    "color": "#cc00cc",
}
metric_info["reply_NXDOMAIN"] = {
    "title": _("reply NXDOMAIN"),
    "unit": "count",
    "color": "#cc9900",
}
metric_info["reply_CNAME"] = {
    "title": _("reply CNAME"),
    "unit": "count",
    "color": "#009933",
}
metric_info["reply_IP"] = {
    "title": _("reply IP"),
    "unit": "count",
    "color": "#3333ff",
}
graph_info["dns_query_types"] = {
    "title":
    _("DNS Query Types"),
    "metrics": [
        ("dns_queries_all_types", "area"),
        ("reply_NODATA", "area"),
        ("reply_NXDOMAIN", "area"),
        ("reply_CNAME", "area"),
        ("reply_IP", "area"),
    ],
}
