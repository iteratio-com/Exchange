#!/usr/bin/env python3

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
)

from .utils.rubrik_api import RubrikSection, parse_rubrik_single


def host_label_rubrik_node(section: RubrikSection) -> HostLabelGenerator:
    if section and section.get("brikId"):
        yield HostLabel("rubrikDevice", "node")


agent_section_rubrik_node = AgentSection(
    name="rubrik_node",
    parse_function=parse_rubrik_single,
    host_label_function=host_label_rubrik_node,
)


def discover_rubrik_cluster_node(section: RubrikSection) -> DiscoveryResult:
    if section:
        yield Service()


def check_rubrik_cluster_node(section: RubrikSection) -> CheckResult:
    if not section:
        return

    yield Result(
        state=State.OK if section["status"] == "OK" else State.CRIT,
        summary=f"Node: {section['hostname']}, State: {section['status']}",
        details=f"IP: {section['ipAddress']}\nbrikId: {section['brikId']}",
    )
    yield Result(
        state=State.OK if not section["hasUnavailableDisks"] else State.CRIT,
        summary=f"Unavailable disks: {section['hasUnavailableDisks']}",
    )


check_plugin_rubrik_node = CheckPlugin(
    name="rubrik_node",
    service_name="Rubrik Node Status",
    discovery_function=discover_rubrik_cluster_node,
    check_function=check_rubrik_cluster_node,
)
