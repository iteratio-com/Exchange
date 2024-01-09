#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# 2023, marcus.klein@iteratio.com

from .agent_based_api.v1 import HostLabel, Result, Service, State, register
from .agent_based_api.v1.type_defs import CheckResult, DiscoveryResult, HostLabelGenerator
from .utils.rubrik_api import RubrikSection, parse_rubrik


def host_label_rubrik_cluster(section: RubrikSection) -> HostLabelGenerator:
    if section.get("status"):
        yield HostLabel("rubrikDevice", "cluster")


register.agent_section(
    name="rubrik_cluster_system_status",
    parse_function=parse_rubrik,
    host_label_function=host_label_rubrik_cluster,
)


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


register.check_plugin(
    name="rubrik_cluster_system_status",
    service_name="Rubrik Cluster System Status",
    discovery_function=discover_rubrik_cluster_system_status,
    check_function=check_rubrik_cluster_system_status,
)
