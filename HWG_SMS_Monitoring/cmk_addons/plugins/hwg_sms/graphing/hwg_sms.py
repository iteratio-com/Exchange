#!/usr/bin/env python3

from cmk.graphing.v1 import graphs, metrics, perfometers, Title

UNIT_PERCENTAGE = metrics.Unit(metrics.DecimalNotation("%"))
UNIT_COUNT = metrics.Unit(metrics.DecimalNotation(""))
UNIT_DECIBEL_MILLIWATTS = metrics.Unit(metrics.DecimalNotation("dBm"))

metric_hwg_rssi = metrics.Metric(
    name="rssi",
    title=Title("Received Signal Strength Indicator (RSSI)"),
    unit=UNIT_COUNT,
    color=metrics.Color.DARK_CYAN,
)
metric_hwg_signal_quality = metrics.Metric(
    name="signal_quality",
    title=Title("Signal Quality"),
    unit=UNIT_PERCENTAGE,
    color=metrics.Color.BLUE,
)
metric_hwg_msg_queue_length = metrics.Metric(
    name="msg_queue_length",
    title=Title("Message Queue Length"),
    unit=UNIT_COUNT,
    color=metrics.Color.YELLOW,
)
metric_hwg_failed_sms = metrics.Metric(
    name="failed_sms",
    title=Title("Faild SMS"),
    unit=UNIT_COUNT,
    color=metrics.Color.RED,
)
metric_hwg_send_sms = metrics.Metric(
    name="send_sms",
    title=Title("Send SMS"),
    unit=UNIT_COUNT,
    color=metrics.Color.GREEN,
)
metric_hwg_bit_error_rate = metrics.Metric(
    name="bit_error_rate",
    title=Title("Bit-Error-Rate (BER)"),
    unit=UNIT_COUNT,
    color=metrics.Color.PURPLE,
)

metric_hwg_singal_strength = metrics.Metric(
    name="singal_strength",
    title=Title("Signal Quality"),
    unit=UNIT_DECIBEL_MILLIWATTS,
    color=metrics.Color.PINK,
)

graph_hwg_sms_statistics = graphs.Graph(
    name="sms_statistics",
    title=Title("SMS Statistics"),
    compound_lines=["send_sms"],
    simple_lines=[
        "failed_sms",
    ],
)

perfometer_hwg_signal_quality = perfometers.Perfometer(
    name="signal_quality",
    focus_range=perfometers.FocusRange(
        perfometers.Closed(0),
        perfometers.Closed(
            metrics.MaximumOf(
                "signal_quality",
                metrics.Color.GRAY,
            )
        ),
    ),
    segments=["signal_quality"],
)
perfometer_hwg_msg_queue_length = perfometers.Perfometer(
    name="msg_queue_length",
    focus_range=perfometers.FocusRange(
        perfometers.Closed(0),
        perfometers.Closed(
            metrics.MaximumOf(
                "msg_queue_length",
                metrics.Color.GRAY,
            )
        ),
    ),
    segments=["msg_queue_length"],
)
perfometer_hwg_sms_statistics = perfometers.Bidirectional(
    name="hwg_sms_statistics",
    left=perfometers.Perfometer(
        name="send_sms",
        focus_range=perfometers.FocusRange(
            perfometers.Closed(0),
            perfometers.Closed(100),
        ),
        segments=["send_sms"],
    ),
    right=perfometers.Perfometer(
        name="failed_sms",
        focus_range=perfometers.FocusRange(
            perfometers.Closed(0),
            perfometers.Closed(100),
        ),
        segments=["failed_sms"],
    ),
)
