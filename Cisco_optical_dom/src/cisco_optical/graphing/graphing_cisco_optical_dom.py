from cmk.graphing.v1 import Title
from cmk.graphing.v1.graphs import Graph, MinimalRange
from cmk.graphing.v1.metrics import Color, DecimalNotation, Metric, StrictPrecision, Unit

UNIT_DBM = Unit(DecimalNotation("dBm"), StrictPrecision(2))

_COLORS = (
    Color.BLUE,
    Color.GREEN,
    Color.ORANGE,
    Color.PURPLE,
    Color.CYAN,
    Color.YELLOW,
    Color.PINK,
    Color.BROWN,
)


for _lane, _color in enumerate(_COLORS, start=1):
    globals()[f"metric_cisco_optical_rx_power_lane_{_lane}"] = Metric(
        name=f"cisco_optical_rx_power_lane_{_lane}",
        title=Title(f"RX power lane {_lane}"),
        unit=UNIT_DBM,
        color=_color,
    )
    globals()[f"metric_cisco_optical_tx_power_lane_{_lane}"] = Metric(
        name=f"cisco_optical_tx_power_lane_{_lane}",
        title=Title(f"TX power lane {_lane}"),
        unit=UNIT_DBM,
        color=_color,
    )

_RX = [f"cisco_optical_rx_power_lane_{lane}" for lane in range(1, 9)]
_TX = [f"cisco_optical_tx_power_lane_{lane}" for lane in range(1, 9)]


graph_cisco_optical_rx_power = Graph(
    name="cisco_optical_rx_power",
    title=Title("Optical RX power"),
    minimal_range=MinimalRange(-20.0, 5.0),
    simple_lines=_RX,
    optional=_RX[1:],
)

graph_cisco_optical_tx_power = Graph(
    name="cisco_optical_tx_power",
    title=Title("Optical TX power"),
    minimal_range=MinimalRange(-20.0, 5.0),
    simple_lines=_TX,
    optional=_TX[1:],
)
