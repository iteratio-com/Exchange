#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# 2023, marcus.klein@iteratio.com

from .agent_based_api.v1 import (
    register,
    Result,
    Service,
    State,
    check_levels,
    Metric,
)


def parse_mshpc_nodes(string_table):
    out = {}
    for elem in string_table:
        try:
            out.update(eval(elem[0]))
        except:
            pass
    return out


register.agent_section(
    name="mshpc_nodes",
    parse_function=parse_mshpc_nodes,
)


def discover_mshpc_nodes(section):
    if section:
        yield Service()


def check_mshpc_nodes(params, section):
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data from host")
        return

    nodes_total = 0

    for key, value in section.get("State", {}).items():
        levels = params.get(f"nodes_{key.lower()}", {})
        nodes_total += value
        yield from check_levels(
            value,
            levels_upper=levels.get("upper"),
            levels_lower=levels.get("lower"),
            metric_name=f"mshpc_nodes_state_{key.lower()}",
            render_func=int,
            label=key,
        )

    levels = params.get("nodes_reachable", None)
    yield from check_levels(
        section.get("Reachable", {}).get("True", 0),
        levels_lower=params.get("nodes_reachable", (None, None)),
        metric_name="mshpc_nodes_state_reachable",
        render_func=int,
        label="Reachable",
    )

    levels = params.get("nodes_unreachable", None)
    yield from check_levels(
        section.get("Reachable", {}).get("False", 0),
        levels_upper=params.get("nodes_unreachable", (None, None)),
        metric_name="mshpc_nodes_state_not_reachable",
        render_func=int,
        # notice_only=True,
        label="Not reachable",
    )

    yield Metric("MSHPC_Nodes_Total", nodes_total)
    yield Result(state=State.OK, summary=f"Nodes total: {nodes_total}")


register.check_plugin(
    name="mshpc_nodes",
    service_name="MSHPC Nodes",
    discovery_function=discover_mshpc_nodes,
    check_function=check_mshpc_nodes,
    check_default_parameters={},
    check_ruleset_name="mshpc_nodes",
)
