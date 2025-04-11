#!/usr/bin/env python3


from cmk.agent_based.v2 import (
    check_levels,
    CheckPlugin,
    CheckResult,
    contains,
    DiscoveryResult,
    render,
    Service,
    SimpleSNMPSection,
    SNMPTree,
    StringTable,
    State,
    Result,
)

from typing import Any
from collections.abc import Mapping

HWGSMSSection = dict[str, str | int]


def saveint(v: str) -> int:
    try:
        v = int(v)
    except:
        v = 0
    return v


def parse_hwg_sms(string_table: StringTable) -> HWGSMSSection:
    (
        reg,
        operator,
        strength,
        quality,
        sms,
        fail_sms,
        msg_length,
        rssi,
        ber,
    ) = string_table[0]
    return {
        "reg": reg,
        "operator": operator,
        "signal_strength": saveint(strength),
        "signal_quality": saveint(quality),
        "sms": saveint(sms),
        "failed_sms": saveint(fail_sms),
        "msg_length": saveint(msg_length),
        "rssi": saveint(rssi),
        "ber": saveint(ber),
    }


snmp_section_hwg_sms = SimpleSNMPSection(
    name="hwg_sms",
    detect=contains(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.21796.4.10"),  # System ObjectID
    parse_function=parse_hwg_sms,
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.21796.4.10.1",
        oids=[
            "2",  # Modem Network Registration
            "3",  # Operator Name
            "4",  # Signal Strength
            "5",  # Signal Quality
            "6",  # Number SMS
            "7",  # Number of Faild SMS
            "10",  # Message Queue length
            "11",  # RSSI
            "12",  # BER
        ],
    ),
)


def discover_hwg_sms_status(section: HWGSMSSection) -> DiscoveryResult:
    if section and section.get("reg") and section.get("operator"):
        yield Service()


def check_hwg_sms_status(section: HWGSMSSection) -> CheckResult:
    if not (section.get("reg") and section.get("operator")):
        yield Result(state=State.UNKNOWN, summary="Informations are Missing")
        return

    yield Result(
        state=State.OK if section.get("reg").startswith("Registered") else State.CRIT,
        summary=f"Staus: {section.get('reg')}",
    )
    yield Result(state=State.OK, summary=f"Operator: {section.get('operator')}")


check_plugin_hwg_sms_status = CheckPlugin(
    name="hwg_sms_status",
    sections=["hwg_sms"],
    service_name="SMS GW Status",
    discovery_function=discover_hwg_sms_status,
    check_function=check_hwg_sms_status,
)


def discover_hwg_sms_signal(section: HWGSMSSection) -> DiscoveryResult:
    if section and section.get("signal_strength") != None and section.get("signal_quality") != None:
        yield Service()


def check_hwg_sms_signal(params: Mapping[str, Any], section: HWGSMSSection) -> CheckResult:
    if not section:
        return

    yield from check_levels(
        section.get("signal_strength"),
        levels_lower=params.get("signal_strength"),
        metric_name="singal_strength",
        label="Signal strength",
        render_func=lambda v: "%d dBm" % v,
    )
    yield from check_levels(
        section.get("signal_quality"),
        levels_lower=params.get("signal_quality"),
        metric_name="signal_quality",
        label="Signal Quality",
        render_func=render.percent,
    )
    rssi = section.get("rssi")

    if rssi == 0:
        txt = "No Signal"
    elif rssi in range(1, 10):
        txt = "very low Signal"
    elif rssi in range(10, 20):
        txt = "low Signal"
    elif rssi in range(20, 30):
        txt = "good Signal"
    elif rssi in range(30, 40):
        txt = "very good Signal"
    elif rssi in range(40, 46):
        txt = "excellent Signal"
    else:
        txt = "Unknown Signal value"

    yield from check_levels(
        rssi,
        metric_name="rssi",
        label="RSSI",
        render_func=lambda v: "%d (%s)" % (v, txt),
    )
    yield from check_levels(
        section.get("ber"),
        metric_name="bit_error_rate",
        label="Bit error rate",
        render_func=int,
    )


check_plugin_hwg_sms_signal = CheckPlugin(
    name="hwg_sms_signal",
    sections=["hwg_sms"],
    service_name="SMS GW Signal",
    discovery_function=discover_hwg_sms_signal,
    check_function=check_hwg_sms_signal,
    check_default_parameters={
        "signal_quality": ("fixed", (30.0, 10.0)),
        "signal_strength": ("fixed", (-85, -95)),
    },
    check_ruleset_name="sms_gw_signal",
)


def discover_hwg_sms_msg_queue(section: HWGSMSSection) -> DiscoveryResult:
    if section.get("msg_length") != None:
        yield Service()


def check_hwg_sms_msg_queue(section: HWGSMSSection) -> CheckResult:
    if not section:
        return

    yield from check_levels(
        section.get("msg_length"),
        metric_name="msg_queue_length",
        label="Message Queue",
        render_func=int,
    )


check_plugin_hwg_sms_msg_queue_length = CheckPlugin(
    name="hwg_sms_msg_queue_length",
    sections=["hwg_sms"],
    service_name="SMS GW Message Queue",
    discovery_function=discover_hwg_sms_msg_queue,
    check_function=check_hwg_sms_msg_queue,
)


def discover_hwg_sms_statistics(section: HWGSMSSection) -> DiscoveryResult:
    if section:
        yield Service()


def check_hwg_sms_statistics(section: HWGSMSSection) -> CheckResult:
    if not section:
        return

    yield from check_levels(
        section.get("sms"),
        metric_name="send_sms",
        label="Send SMS",
        render_func=int,
    )
    yield from check_levels(
        section.get("failed_sms"),
        metric_name="failed_sms",
        label="Failed SMS",
        render_func=int,
    )


check_plugin_hwg_sms_statistics = CheckPlugin(
    name="hwg_sms_statistics",
    sections=["hwg_sms"],
    service_name="SMS GW Statistics",
    discovery_function=discover_hwg_sms_statistics,
    check_function=check_hwg_sms_statistics,
)
