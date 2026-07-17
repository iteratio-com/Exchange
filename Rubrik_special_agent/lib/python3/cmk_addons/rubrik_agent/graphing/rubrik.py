#!/usr/bin/env python3

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

UNIT_BYTES_PER_SECOND = Unit(IECNotation("B/s"))

metric_rubrik_bandwidth = Metric(
    name="rubrik_bandwidth",
    title=Title("Average archive bandwidth last hour"),
    unit=UNIT_BYTES_PER_SECOND,
    color=Color.PINK,
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
