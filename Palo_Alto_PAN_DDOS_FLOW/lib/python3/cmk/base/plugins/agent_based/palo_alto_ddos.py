#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .agent_based_api.v1 import register, Service, SNMPTree, contains, State, Result, check_levels
from .agent_based_api.v1.type_defs import StringTable, CheckResult, DiscoveryResult
from typing import Dict, Any, Mapping

Section = Dict[str, str]


def parse_palo_alto_ddos(string_table: StringTable) -> Section:
    if j := string_table[0]:
        return {
            "dos_blk_num_entries": j[0],
            "policy_deny": j[1],
            "dos_drop_ip_blocked": j[2],
            "flow_dos_rule_drop": j[3],
            "dos_blk_sw_entries": j[4],
            "dos_blk_hw_entries": j[5],
        }


register.snmp_section(
    name="palo_alto_ddos",
    parse_function=parse_palo_alto_ddos,
    detect=contains(".1.3.6.1.2.1.1.2.0", "25461"),
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.25461.2.1.2.1.19.8",
        oids=[
            "2",  # flow_dos_blk_num_entries
            "10",  # flow_policy_deny
            "13",  # flow_dos_drop_ip_blocked
            "23",  # flow_dos_rule_drop
            "33",  # flow_dos_blk_sw_entries
            "34",  # flow_dos_blk_hw_entries
        ],
    ),
)


def discover_palo_alto_ddos(section: Section) -> DiscoveryResult:
    if section:
        yield Service()


def check_palo_alto_ddos(params: Mapping[str, Any], section: Section) -> CheckResult:
    if not section:
        yield Result(state=State.UNKNOWN, summary="No Data")
        return

    info = (
        ("DOS Hardware block table", "dos_blk_hw_entries"),
        ("DOS block table Entries", "dos_blk_num_entries"),
        ("DOS Software block table", "dos_blk_sw_entries"),
        (
            "Packets dropped by Flagged for blocking and under block duration by other",
            "dos_drop_ip_blocked",
        ),
        ("Packets dropped by Rate limited or IP blocked", "flow_dos_rule_drop"),
        ("Session denied by policy", "policy_deny"),
    )

    for i, j in info:
        yield from check_levels(
            float(section.get(j, 0)),
            levels_upper=params.get(j),
            metric_name=j,
            label=i,
            render_func=lambda v: "%.0f" % v,
        )


register.check_plugin(
    name="palo_alto_ddos",
    service_name="Flow DOS",
    discovery_function=discover_palo_alto_ddos,
    check_function=check_palo_alto_ddos,
    check_default_parameters={},
    check_ruleset_name="palo_alto_ddos",
)
