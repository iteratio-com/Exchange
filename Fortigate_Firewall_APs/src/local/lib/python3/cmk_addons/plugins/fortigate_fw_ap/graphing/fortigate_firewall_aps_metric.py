#!/usr/bin/env python3


from cmk.graphing.v1 import metrics, Title, graphs
from cmk.graphing.v1.perfometers import Closed, FocusRange, Open, Perfometer

UNIT_COUNTER = metrics.Unit(metrics.DecimalNotation(""), metrics.StrictPrecision(2))
metric_5ghz_clients = metrics.Metric(
    name="5ghz_clients",
    title=Title("Client connects for 5 Ghz band"),
    unit=UNIT_COUNTER,
    color=metrics.Color.DARK_PINK,
)
metric_24ghz_clients = metrics.Metric(
    name="24ghz_clients",
    title=Title("Client connects for 2,4 Ghz band"),
    unit=UNIT_COUNTER,
    color=metrics.Color.ORANGE,
)

metric_6ghz_clients = metrics.Metric(
    name="6ghz_clients",
    title=Title("Client connects for 6 Ghz band"),
    unit=UNIT_COUNTER,
    color=metrics.Color.GREEN,
)
metric_connected_clients = metrics.Metric(
    name="connected_clients",
    title=Title("Client connected (all Connections)"),
    unit=UNIT_COUNTER,
    color=metrics.Color.DARK_BROWN,
)

graph_fortigate_clients = graphs.Graph(
    name="fortigate_clients",
    title=Title("Connected clients"),
    compound_lines=["connected_clients", "24ghz_clients", "5ghz_clients", "6ghz_clients"],
)

perfometer_fortigate_clients = Perfometer(
    name="connected_clients",
    focus_range=FocusRange(
        Closed(0),
        Open(50.0),
    ),
    segments=["connected_clients"],
)
