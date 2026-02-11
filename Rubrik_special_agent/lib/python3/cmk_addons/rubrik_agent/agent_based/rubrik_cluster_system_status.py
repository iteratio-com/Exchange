#!/usr/bin/env python3

from ast import literal_eval
from typing import Any

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    HostLabel,
    HostLabelGenerator,
    Result,
    Service,
    State,
    StringTable,
)

RubrikSection = dict[str, Any]


def parse_rubrik_single(string_table: StringTable) -> RubrikSection:
    """Parse single rubrik cluster section."""
    try:
        out = literal_eval("".join([i[0] for i in string_table]))
        return out if isinstance(out, dict) else {}
    except ValueError:
        return {}


def host_label_rubrik_cluster(section: RubrikSection) -> HostLabelGenerator:
    if section and section.get("status"):
        yield HostLabel("rubrikDevice", "cluster")


def discover_rubrik_cluster_system_status(section: RubrikSection) -> DiscoveryResult:
    if section:
        yield Service()


def check_rubrik_cluster_system_status(section: RubrikSection) -> CheckResult:
    if not section:
        return

    status = section["status"].upper()

    yield Result(
        state=State.OK if status == "OK" else State.CRIT,
        summary=f"Status: {status}",
    )
    if msg := section.get("message"):
        yield Result(
            state=State.OK,
            summary=f"Message: {msg}",
        )
    if affected := section.get("affectedNodeIds"):
        yield Result(
            state=State.OK,
            summary=f"Affected Nodes: {', '.join(affected)}",
        )


agent_section_rubrik_cluster_system_status = AgentSection(
    name="rubrik_cluster_system_status",
    parse_function=parse_rubrik_single,
    host_label_function=host_label_rubrik_cluster,
)

check_plugin_rubrik_cluster_system_status = CheckPlugin(
    name="rubrik_cluster_system_status",
    service_name="Rubrik Cluster System Status",
    discovery_function=discover_rubrik_cluster_system_status,
    check_function=check_rubrik_cluster_system_status,
)
