#!/usr/bin/env python3

from typing import Dict, List, Mapping, Any
from .agent_based_api.v1 import (
    exists,
    any_of,
    register,
    Result,
    Service,
    SNMPTree,
    State,
    all_of,
    contains,
    HostLabel,
    render,
)
from .agent_based_api.v1.type_defs import (
    CheckResult,
    StringTable,
    DiscoveryResult,
    HostLabelGenerator,
)

CiscoSyncSection = Dict[str, Any]

DETECTCISCOSYNCE = all_of(
    any_of(
        contains(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.9.1.3009"),
        contains(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.9.1.2678"),
        contains(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.9.1.2571"),
    ),
    exists(".1.3.6.1.4.1.9.9.761.1.1.2.1.2.*"),
)


def parse_cisco_sync(string_table: List[StringTable]) -> CiscoSyncSection:
    parsed = {}
    current_active, supported = string_table
    for name, int_type, quality, prio, connection_time in current_active:
        if int_type == "3":
            parsed["selected"] = {
                "name": name,
                "type": int_type,
                "quality": quality,
                "prio": prio,
                "time": int(connection_time) if connection_time else None,
            }
    for name, int_type in supported:
        if int_type == "3":
            parsed.setdefault("supported", []).append(name)
    return parsed if parsed.get("selected") else None


def discover_cisco_sync_e_label(section: CiscoSyncSection) -> HostLabelGenerator:
    if section:
        yield HostLabel("cisco", "sync-e")


register.snmp_section(
    name="cisco_sync_e",
    parse_function=parse_cisco_sync,
    host_label_function=discover_cisco_sync_e_label,
    fetch=[
        SNMPTree(
            base=".1.3.6.1.4.1.9.9.761.1.1.2.1",
            oids=[
                "2",  # Name
                "3",  # Type
                "4",  # Quality level
                "5",  # Priority
                "6",  # Connection time
            ],
        ),
        SNMPTree(
            base=".1.3.6.1.4.1.9.9.761.1.1.3.1",
            oids=[
                "2",  # Name
                "3",  # Type
            ],
        ),
    ],
    detect=DETECTCISCOSYNCE,
)


def discover_cisco_synce(section: CiscoSyncSection) -> DiscoveryResult:
    if section:
        yield Service(parameters={"discovered_selected": section.get("selected", {}).get("name")})


def check_cisco_synce(params: Mapping[str, Any], section: DETECTCISCOSYNCE) -> CheckResult:
    if not section.get("selected", {}):
        yield Result(state=State.UNKNOWN, summary="No Data aviable")
        return

    selected = section.get("selected", {})

    if selected.get("name") == params.get("discovered_selected"):
        yield Result(state=State.OK, summary=f"Running on Interface: {selected.get('name')}")
    else:
        yield Result(
            state=State(params.get("state_interface_changed", 2)),
            summary=f"Changed Interface, from {params.get('discovered_selected')} to {selected.get('name')}",
        )

    quality_state, quality_txt = {
        "1": (State.CRIT, "NULL"),
        "2": (State.CRIT, "Do not use for synchronization (DNU)"),
        "3": (State.CRIT, "Do not use for synchronization (DUS)"),
        "4": (State.CRIT, "Signal failure state (FAILED)"),
        "5": (State.CRIT, "Unallocated SSM value (INV0)"),
        "6": (State.CRIT, "Unallocated SSM value (INV1)"),
        "7": (State.CRIT, "Unallocated SSM value (INV2)"),
        "8": (State.CRIT, "Unallocated SSM value (INV3)"),
        "9": (State.CRIT, "Unallocated SSM value (INV4)"),
        "10": (State.CRIT, "Unallocated SSM value (INV5)"),
        "11": (State.CRIT, "Unallocated SSM value (INV6)"),
        "12": (State.CRIT, "Unallocated SSM value (INV7)"),
        "13": (State.CRIT, "Unallocated SSM value (INV8)"),
        "14": (State.CRIT, "Unallocated SSM value (INV9)"),
        "15": (State.CRIT, "Unallocated SSM value (INV10)"),
        "16": (State.CRIT, "Unallocated SSM value (INV11)"),
        "17": (State.CRIT, "Unallocated SSM value (INV12)"),
        "18": (State.CRIT, "Unallocated SSM value (INV13)"),
        "19": (State.CRIT, "Unallocated SSM value (INV14)"),
        "20": (State.CRIT, "Unallocated SSM value (INV15)"),
        "21": (State.CRIT, "Not supporting the SSM processing (NSUPP)"),
        "22": (State.OK, "Primary reference clock (PRC)"),
        "23": (State.CRIT, "Provisionable by the network operator (PROV)"),
        "24": (State.CRIT, "PRS traceable (PRS)"),
        "25": (State.CRIT, "Synchronous equipment clock (SEC)"),
        "26": (State.CRIT, "SONET clock self timed (SMC)"),
        "27": (State.CRIT, "Type I or V slave clock defined in ITU-T G.811 (SSUA)"),
        "28": (State.CRIT, "Type VI slave clock defined in ITU-T G.812 (SSUB)"),
        "29": (State.CRIT, "Stratum 2 (ST2)"),
        "30": (State.CRIT, "Stratum 3 (ST3)"),
        "31": (State.CRIT, "Stratum 3E (ST3E)"),
        "32": (State.CRIT, "Stratum 4 freerun (ST4)"),
        "33": (State.CRIT, "Synchronized; traceability unknown (STU)"),
        "34": (State.CRIT, "Transit node clock (TNC)"),
        "35": (State.CRIT, "Unconnected to an input (UNC)"),
        "36": (State.CRIT, "Unknown clock source (UNK)"),
    }.get(selected.get("quality"), (State.UNKNOWN, "Unknown Quality Status"))

    yield Result(state=quality_state, summary=f"Quality Level: {quality_txt}")
    yield Result(state=State.OK, summary=f"Priority: {selected.get('prio')}")
    if t := selected.get("time"):
        yield Result(state=State.OK, notice=f"Time: {render.timespan(t)}")

    # Check Amount of Possible Interfaces
    if section.get("supported") and len(section.get("supported")) >= params.get(
        "synceinteraces", 2
    ):
        yield Result(
            state=State.OK,
            summary=f"Possible Interfaces: {len(section.get('supported'))}",
            details=f"Possible Interfaces: {', '.join(section.get('supported'))}",
        )
    else:
        yield Result(
            state=State(params.get("state_amound_interfaces")),
            summary=f"Possible Interfaces: {len(section.get('supported'))} but there should be {params.get('synceinteraces', 2)} ({', '.join(section.get('supported'))})",
        )


register.check_plugin(
    name="cisco_sync_e",
    service_name="Cisco Sync-E",
    discovery_function=discover_cisco_synce,
    check_function=check_cisco_synce,
    check_default_parameters={
        "synceinteraces": 2,
        "state_amound_interfaces": 1,
        "state_interface_changed": 2,
    },
    check_ruleset_name="cisco_sync_e_group",
)
