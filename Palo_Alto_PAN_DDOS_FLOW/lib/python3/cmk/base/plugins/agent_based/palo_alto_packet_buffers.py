#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .agent_based_api.v1 import register, Service, SNMPTree, contains, get_value_store
from .agent_based_api.v1.type_defs import StringTable, CheckResult, DiscoveryResult
from .utils.df import df_check_filesystem_list

from typing import List, Tuple, Any, Mapping
from contextlib import suppress



Section = List[Tuple[str, int, float, float]]


def parse_palo_alto_packet_buffers(string_table: StringTable) -> Section:
    def _to_mb(raw: str, unit_size: int) -> float:
        unscaled = int(raw)
        if unscaled < 0:
            unscaled += 2**32
        return unscaled * unit_size / 1048576.0

    def _to_bytes(units: str) -> int:
        """In some cases instead of a plain byte-count an extra quantifier is appended
        e.g. '4096 Bytes' instead of just '4096'"""
        components = units.split(" ", 1)
        factor = 1 if len(components) == 1 or components[1] != "KBytes" else 1024
        return int(components[0]) * factor

    parsed = []
    for hrtype, hrdescr, hrunits, hrsize, hrused in string_table:
        if hrtype != '.1.3.6.1.2.1.25.2.1.1':
            continue
        with suppress(ValueError):
            units = _to_bytes(hrunits)
            size = _to_mb(hrsize, units)
            used = _to_mb(hrused, units)
            parsed.append((hrdescr, int(hrunits), size - used, 0))
    return parsed


register.snmp_section(
    name="palo_alto_packet_buffers",
    parse_function=parse_palo_alto_packet_buffers,
    detect=contains(".1.3.6.1.2.1.1.2.0", "25461"),
    fetch=SNMPTree(
        base=".1.3.6.1.2.1.25.2.3.1",
        oids=[
            "2",  # hrStorageType
            "3",  # hrStorageDescr
            "4",  # hrStorageAllocationUnits
            "5",  # hrStorageSize
            "6",  # hrStorageUsed 
        ]),
)


def discover_palo_alto_packet_buffers(section: Section) -> DiscoveryResult:
    for i in section:
        yield Service(item=i[0])


def check_palo_alto_packet_buffers(item: str, params: Mapping[str, Any],
                                   section: Section) -> CheckResult:
    yield from df_check_filesystem_list(
        value_store=get_value_store(),
        item=item,
        params=params,
        fslist_blocks=section,
    )


register.check_plugin(
    name="palo_alto_packet_buffers",
    service_name="Buffers %s",
    discovery_function=discover_palo_alto_packet_buffers,
    check_function=check_palo_alto_packet_buffers,
    check_default_parameters={},
    check_ruleset_name="filesystem",
)