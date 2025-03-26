#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections.abc import Mapping

# from typing import Any Mapping
from time import time
from typing import Any
from dataclasses import dataclass

from cmk.agent_based.v2 import (
    check_levels,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    contains,
    get_rate,
    get_value_store,
    render,
    Service,
    SNMPSection,
    SNMPTree,
    StringTable,
    Result,
    Metric,
    OIDEnd,
    State,
)

from cmk.plugins.lib.cpu_util import check_cpu_util


@dataclass
class AccessPoint:
    """Access Point data class."""

    admin_state: str
    name: str
    location: str
    connection_state: str
    profile_name: str
    model_number: str
    hw_version: str
    sw_version: str
    connected_clients: int
    rx: int
    tx: int
    cpu_usage: float
    memory_usage: float
    connected_24GHz: int
    connected_5GHz: int
    connected_6GHz: int


SectionFortigateFirewallAPS = dict[str, AccessPoint]


def saveint(i: str) -> int:
    try:
        return int(i)
    except (TypeError, ValueError):
        return 0


def savefloat(i: str) -> float:
    try:
        return float(i)
    except (TypeError, ValueError):
        return 0


def parse_fortigate_firewall_aps(string_table: list[StringTable]) -> SectionFortigateFirewallAPS:
    if len(string_table) != 3 or not string_table[0]:
        return
    parsed = {}
    lookup_fequences = {i: j for i, j in string_table[2]}
    secound_infos = {i: j for i, *j in string_table[1]}
    for oid, idx, admin, name, location in string_table[0]:
        (
            connection_state,
            profile_name,
            model_number,
            hw_version,
            sw_version,
            connected_clients,
            rx,
            tx,
            cpu_usage,
            mem_usage,
        ) = secound_infos.get(oid)
        parsed[idx] = AccessPoint(
            admin_state=admin,
            name=name,
            location=location,
            connection_state=connection_state,
            profile_name=profile_name,
            model_number=model_number,
            hw_version=hw_version,
            sw_version=sw_version,
            connected_clients=saveint(connected_clients),
            rx=saveint(rx),
            tx=saveint(tx),
            cpu_usage=savefloat(cpu_usage),
            memory_usage=savefloat(mem_usage),
            connected_24GHz=saveint(lookup_fequences.get(f"{oid}.1", "0")),
            connected_5GHz=saveint(lookup_fequences.get(f"{oid}.2", "0")),
            connected_6GHz=saveint(lookup_fequences.get(f"{oid}.3", "0")),
        )
    return parsed


snmp_section_fortigate_firewall_aps = SNMPSection(
    name="fortigate_firewall_aps",
    parse_function=parse_fortigate_firewall_aps,
    detect=contains(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.12356.101.1.2010"),
    fetch=[
        SNMPTree(base=".1.3.6.1.4.1.12356.101.14.4.3.1", oids=[OIDEnd(), "1", "2", "3", "4"]),
        SNMPTree(
            base=".1.3.6.1.4.1.12356.101.14.4.4.1",
            oids=[OIDEnd(), "7", "11", "12", "13", "14", "17", "18", "19", "20", "21"],
        ),
        SNMPTree(base=".1.3.6.1.4.1.12356.101.14.4.5.1", oids=[OIDEnd(), "9"]),
    ],
)


def discover_fortigate_firewall_aps(section: SectionFortigateFirewallAPS) -> DiscoveryResult:
    for ap in section:
        yield Service(item=ap)


def check_fortigate_firewall_aps(
    item: str, params: Mapping[str, Any], section: SectionFortigateFirewallAPS
) -> CheckResult:
    if not (ap := section.get(item)):
        return

    admin = {"1": "Discovered", "2": "Disable", "3": "Enable", "0": "Other"}.get(
        ap.admin_state, "unknown"
    )

    yield Result(
        state=State(params["admin_state"].get(ap.admin_state, 3)),
        summary=(
            f"[{ap.name}] Location: {ap.location}, Operational: {admin}"
            if ap.location
            else f"[{ap.name}] Operational: {admin}"
        ),
    )

    availability = {
        "0": "Other",
        "1": "Offline",
        "2": "Online",
        "3": "Downloading Image",
        "4": "Connected Image",
    }.get(ap.connection_state, "unknown")

    yield Result(
        state=State(params["availability"].get(ap.connection_state, 3)),
        summary=f"Availability: {availability}",
    )
    yield Result(state=State.OK, summary=f"Connected Clients: {ap.connected_clients}")
    yield Metric("connected_clients", ap.connected_clients)

    yield Result(state=State.OK, notice=f"Connected Clients in 2.4GHz: {ap.connected_24GHz}")
    yield Result(state=State.OK, notice=f"Connected Clients in 5GHz: {ap.connected_5GHz}")
    yield Result(state=State.OK, notice=f"Connected Clients in 6GHz: {ap.connected_6GHz}")
    yield Metric("24ghz_clients", ap.connected_24GHz)
    yield Metric("5ghz_clients", ap.connected_5GHz)
    yield Metric("6ghz_clients", ap.connected_6GHz)

    now = time()
    for sub_result in check_cpu_util(
        util=ap.cpu_usage,
        this_time=now,
        value_store=get_value_store(),
        params=params.get("cpu_util", {}),
    ):
        if isinstance(sub_result, Result):
            if sub_result.summary:
                yield Result(state=sub_result.state, notice=sub_result.summary)
            elif sub_result.notice:
                yield Result(state=sub_result.state, notice=sub_result.notice)
        else:
            yield sub_result

    yield from check_levels(
        ap.memory_usage,
        levels_upper=params.get("mem_usage"),
        metric_name="mem_used_percent",
        label="Memory Usage",
        render_func=render.percent,
        notice_only=True,
    )

    in_rate = get_rate(get_value_store(), f"if.{item}.in", now, ap.rx)
    out_rate = get_rate(get_value_store(), f"if.{item}.out", now, ap.tx)
    result_in, metric_in = check_levels(
        in_rate, levels_upper=params.get("in_rate"), metric_name="if_in_bps", label="In Rate"
    )
    result_out, metric_out = check_levels(
        out_rate, levels_upper=params.get("out_rate"), metric_name="if_out_bps", label="out Rate"
    )
    yield Result(
        state=State.worst(result_in.state, result_out.state),
        notice=f"IN/OUT: {render.nicspeed(in_rate)}/{render.nicspeed(out_rate)}",
    )
    yield metric_in
    yield metric_out

    if ap.profile_name:
        yield Result(state=State.OK, notice=f"Profile Name: {ap.profile_name}")
    if ap.model_number:
        yield Result(state=State.OK, notice=f"Model: {ap.model_number}")
    if ap.hw_version:
        yield Result(state=State.OK, notice=f"HW Version: {ap.hw_version}")
    if ap.sw_version:
        yield Result(state=State.OK, notice=f"SW Version: {ap.sw_version}")


check_plugin_fortigate_firewall_aps = CheckPlugin(
    name="fortigate_firewall_aps",
    service_name="AP %s",
    discovery_function=discover_fortigate_firewall_aps,
    check_function=check_fortigate_firewall_aps,
    check_ruleset_name="fortigate_firewall_aps",
    check_default_parameters={
        "admin_state": {"1": 1, "2": 1, "3": 0, "0": 3},
        "availability": {"1": 2, "2": 0, "3": 0, "4": 0, "0": 3},
    },
)
