#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# 2023, marcus.klein@iteratio.com

from .agent_based_api.v1 import HostLabel, Result, Service, State, register
from .agent_based_api.v1.type_defs import CheckResult, DiscoveryResult, HostLabelGenerator
from .utils.rubrik_api import RubrikSection, parse_rubrik


def host_label_rubrik_node(section: RubrikSection) -> HostLabelGenerator:
    if section.get("brikId"):
        yield HostLabel("rubrikDevice", "node")


register.agent_section(
    name="rubrik_node",
    parse_function=parse_rubrik,
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
        state=State.OK if section["hasUnavailableDisks"] == False else State.CRIT,
        summary=f"Unavailable disks: {section['hasUnavailableDisks']}",
    )


register.check_plugin(
    name="rubrik_node",
    service_name="Rubrik Node Status",
    discovery_function=discover_rubrik_cluster_node,
    check_function=check_rubrik_cluster_node,
)
