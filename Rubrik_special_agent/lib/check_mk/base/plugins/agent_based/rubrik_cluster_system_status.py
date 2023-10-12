#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# 2023, marcus.klein@iteratio.com

from .agent_based_api.v1 import (
    register,
    Result,
    Service,
    State,
)

import ast


def parse_rubrik_cluster_system_status(string_table):
    try:
        out = ast.literal_eval(string_table[0][0])
    except:
        out = {}

    return out


register.agent_section(
    name="rubrik_cluster_system_status",
    parse_function=parse_rubrik_cluster_system_status,
)


def discover_rubrik_cluster_system_status(section):
    if section:
        yield Service()


def check_rubrik_cluster_system_status(params, section):
    if not section:
        yield Result(state=State.UNKNOWN, summary="No Data")
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
    check_default_parameters={},
    check_ruleset_name="rubrik_cluster_system_status",
)
