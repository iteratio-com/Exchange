#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from cmk.agent_based.v2 import (
    Service,
    Result,
    exists,
    State,
    CheckPlugin,
    SimpleSNMPSection,
    StringTable,
    DiscoveryResult,
    CheckResult,
    SNMPTree,
)


TAPE_SECTION = dict[str, tuple[str, str]]


def discover_tape_drive_power_supply(section: TAPE_SECTION) -> DiscoveryResult:
    for tape_drive in section:
        yield Service(item=tape_drive)


def parse_dell_emc_ml3_drive_power_supply(string_table: StringTable) -> CheckResult:
    parsed = {}
    for index, ps1, ps2, serialno in string_table:
        if ps1 != "":
            parsed[index + ".1"] = (ps1, serialno)
        if ps2 != "":
            parsed[index + ".2"] = (ps2, serialno)
    return parsed


def check_dell_emc_ml3_drive_power_supply(item: str, section: TAPE_SECTION) -> CheckResult:
    if not section.get(item):
        return

    ps, serialno = section.get(item)

    ps_map = {
        "1": (State.OK, "not installed"),
        "2": (State.OK, "ok"),
        "3": (State.WARN, "not ok"),
    }
    status, txt = ps_map.get(ps, (State.WARN, "unknown Status Code"))

    yield Result(state=status, summary=f"PowerSupply Status: {txt}")
    if serialno:
        yield Result(state=State.OK, summary=f"Chassis SerialNo: {serialno}")


snmp_section_dell_emc_ml3_drive_supply = SimpleSNMPSection(
    name="dell_emc_ml3_drive_supply",
    detect=exists(".1.3.6.1.4.1.14851.3.1.6.2.1.*"),
    parse_function=parse_dell_emc_ml3_drive_power_supply,
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.2.6.257.1.3.2.1",
        oids=[
            "1",  # index
            "3",  # frame power supply 1 status
            "4",  # frame power supply 2 status
            "9",  # serial number
        ],
    ),
)

check_plugin_dell_emc_ml3_drive_supply = CheckPlugin(
    name="dell_emc_ml3_drive_supply",
    service_name="Drive power supply %s",
    discovery_function=discover_tape_drive_power_supply,
    check_function=check_dell_emc_ml3_drive_power_supply,
)
