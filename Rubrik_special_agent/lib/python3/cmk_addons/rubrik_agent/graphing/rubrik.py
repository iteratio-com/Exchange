"""Define Rubrik graphs and translate filesystem metrics from MiB to bytes."""

# +------------------------------------------------------------+
# |                                                            |
# |             | |             | |            | |             |
# |          ___| |__   ___  ___| | ___ __ ___ | | __          |
# |         / __| '_ \ / _ \/ __| |/ / '_ ` _ \| |/ /          |
# |        | (__| | | |  __/ (__|   <| | | | | | |   <         |
# |         \___|_| |_|\___|\___|_|\_\_| |_| |_|_|\_\          |
# |                                   custom code by SVA       |
# |                                                            |
# +------------------------------------------------------------+
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   Copyright (C) 2026 SVA System Vertrieb Alexander GmbH
#                      by leon.buhleier@sva.de


from importlib import import_module

from cmk.graphing.v1 import Title
from cmk.graphing.v1.graphs import Graph
from cmk.graphing.v1.metrics import (
    Color,
    DecimalNotation,
    IECNotation,
    Metric,
    StrictPrecision,
    Unit,
)
from cmk.graphing.v1.perfometers import Bidirectional, FocusRange, Open, Perfometer

_MIB = 1024**2
_FILESYSTEM_TRANSLATIONS = {
    "fs_free": ("fs_free", _MIB),
    "fs_size": ("fs_size", _MIB),
    "fs_used": ("fs_used", _MIB),
    "growth": ("fs_growth", _MIB),
    "trend": ("fs_trend", _MIB),
    "trend_hoursleft": ("trend_hoursleft", 3600),
    "reserved": ("reserved", _MIB),
    "uncommitted": ("uncommitted", _MIB),
    "overprovisioned": ("overprovisioned", _MIB),
}

try:
    from cmk.graphing.v1.translations import PassiveCheck, RenameToAndScaleBy, Translation
except ImportError:
    # Checkmk 2.3/2.4 have no public Translation API; use their legacy registry.
    try:
        _legacy_graphing = import_module("cmk.gui.graphing._legacy")
    except ModuleNotFoundError:
        _legacy_graphing = import_module("cmk.gui.graphing._utils")
    _legacy_graphing.check_metrics["check_mk-rubrik_node_disk"] = {
        name: {"name": target, "scale": scale}
        for name, (target, scale) in _FILESYSTEM_TRANSLATIONS.items()
    }
else:
    translation_rubrik_node_disk = Translation(
        name="rubrik_node_disk",
        check_commands=[PassiveCheck("rubrik_node_disk")],
        translations={
            name: RenameToAndScaleBy(target, scale)
            for name, (target, scale) in _FILESYSTEM_TRANSLATIONS.items()
        },
    )

UNIT_BYTES_PER_SECOND = Unit(IECNotation("B/s"))
UNIT_DAYS = Unit(DecimalNotation(""), StrictPrecision(0))

metric_rubrik_bandwidth = Metric(
    name="rubrik_bandwidth",
    title=Title("Average archive bandwidth last hour"),
    unit=UNIT_BYTES_PER_SECOND,
    color=Color.PINK,
)

metric_rubrik_storage_runway_remaining = Metric(
    name="rubrik_storage_runway_remaining",
    title=Title("Runway remaining (days)"),
    unit=UNIT_DAYS,
    color=Color.ORANGE,
)

metric_rubrik_totalnodes = Metric(
    name="rubrik_totalnodes",
    title=Title("Total nodes count"),
    unit=Unit(DecimalNotation(""), StrictPrecision(0)),
    color=Color.LIGHT_GREEN,
)

metric_rubrik_activenodes = Metric(
    name="rubrik_activenodes",
    title=Title("Active nodes count"),
    unit=Unit(DecimalNotation(""), StrictPrecision(0)),
    color=Color.BLUE,
)

graph_rubrik_nodes_data_combined = Graph(
    name="rubrik_nodes_data",
    title=Title("Rubrik nodes"),
    compound_lines=["rubrik_activenodes"],
    simple_lines=["rubrik_totalnodes"],
    minimal_range=None,
)

perfometer_rubrik_bandwidth = Perfometer(
    name="rubrik_bandwidth",
    focus_range=FocusRange(Open(0), Open(100)),
    segments=["rubrik_bandwidth"],
)

perfometer_rubrik_nodes_data = Bidirectional(
    name="rubrik_nodes_data",
    left=Perfometer(
        name="rubrik_activenodes",
        focus_range=FocusRange(Open(0), Open(100)),
        segments=["rubrik_activenodes"],
    ),
    right=Perfometer(
        name="rubrik_totalnodes",
        focus_range=FocusRange(Open(0), Open(100)),
        segments=["rubrik_totalnodes"],
    ),
)
