#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cmk.gui.i18n import _
from cmk.gui.plugins.metrics import metric_info, graph_info


metric_info["response_time"] = {
    "title": _("Response Time"),
    "unit": "s",
    "color": "35/a",
}
