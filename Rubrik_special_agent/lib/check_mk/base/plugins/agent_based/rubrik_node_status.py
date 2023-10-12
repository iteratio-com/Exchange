#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# 2023, marcus.klein@iteratio.com

from .agent_based_api.v1 import register, Result, Service, State, HostLabel

import ast


def parse_rubrik_cluster_node(string_table):
    if not string_table:
        return {}
    string_table = ast.literal_eval(string_table[0][0])
    return string_table


def host_label_rubrik_node(section):
    if section.get("brikId"):
        yield HostLabel("rubrikNode", "yes")


register.agent_section(
    name="rubrik_node",
    parse_function=parse_rubrik_cluster_node,
    host_label_function=host_label_rubrik_node,
)


def discover_rubrik_cluster_node(section):
    if section:
        yield Service()


def check_rubrik_cluster_node(section):
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data from host")
        return

    yield Result(
        state=State.CRIT if section["status"] != "OK" else State.OK,
        summary=f"Node: {section['hostname']}, State: {section['status']}",
        details=f"IP: {section['ipAddress']}\nbrikId: {section['brikId']}",
    )
    yield Result(
        state=State.CRIT if section["hasUnavailableDisks"] != False else State.OK,
        summary=f"Unavailable disks: {section['hasUnavailableDisks']}",
    )


register.check_plugin(
    name="rubrik_node",
    service_name="Rubrik Node Status",
    discovery_function=discover_rubrik_cluster_node,
    check_function=check_rubrik_cluster_node,
)
