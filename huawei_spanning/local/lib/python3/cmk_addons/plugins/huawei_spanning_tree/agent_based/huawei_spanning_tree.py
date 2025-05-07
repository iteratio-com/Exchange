#!/usr/bin/env python3


from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Service,
    SimpleSNMPSection,
    SNMPTree,
    StringTable,
    State,
    Result,
    OIDBytes,
)


from cmk.plugins.lib.huawei import DETECT_HUAWEI_SWITCH
from dataclasses import dataclass


def mac_address_from_hexstring(hex_value: list[int]) -> str:
    if hex_value:
        out = []
        for x in hex_value[2:]:
            v = hex(x).replace("0x", "").upper()
            if len(v) == 1:
                v = f"0{v}"
            out.append(v)
        return ":".join(out)
    return ""


@dataclass
class SpanningTree:
    status: str
    master_bridge_id: str
    mac_address: str


def parse_huawei_spanning(string_table: StringTable) -> SpanningTree:
    return SpanningTree(
        status=string_table[0][0],
        master_bridge_id=string_table[0][1],
        mac_address=mac_address_from_hexstring(string_table[0][2]),
    )


snmp_section_huawei_spanning = SimpleSNMPSection(
    name="huawei_spanning",
    parse_function=parse_huawei_spanning,
    fetch=SNMPTree(base=".1.3.6.1.4.1.2011.5.25.42.4.1", oids=["1", "2", OIDBytes("5")]),
    detect=DETECT_HUAWEI_SWITCH,
)


def discover_huawei_spanning(section: SpanningTree) -> DiscoveryResult:
    if section:
        yield Service()


def check_huawei_spanning(section: SpanningTree) -> CheckResult:
    if not section:
        return

    yield Result(
        state=State.OK if section.status == "1" else State.CRIT,
        summary=(
            "Spanning Tree is enabled" if section.status == "1" else "Spanning Tree is disabled"
        ),
    )
    if section.mac_address:
        yield Result(state=State.OK, summary=f"Root Bridge: {section.mac_address}")


check_plugin_huawei_spanning = CheckPlugin(
    name="huawei_spanning",
    service_name="Spanning Tree",
    discovery_function=discover_huawei_spanning,
    check_function=check_huawei_spanning,
)
