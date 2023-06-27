#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# 2023, marcus.klein@iteratio.com

from .agent_based_api.v1 import (
    register,
    Result,
    Service,
    State,
    Metric,
)


def parse_mshpc_node_status(string_table):
    out = {}
    for elem in string_table:
        try:
            out.update(eval(elem[0]))
        except:
            pass
    return out


register.agent_section(
    name="mshpc_node_status",
    parse_function=parse_mshpc_node_status,
)


def discover_mshpc_node_status(section):
    if section:
        yield Service()


def check_mshpc_node_status(params, section):
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data from host")
        return

    for key, value in section.items():
        if key == "State":
            yield Result(
                state=State.OK if value == "Online" else State.WARN,
                summary=f"State: {value}",
            )
        elif key == "Reachable":
            yield Result(
                state=State.OK if value == "True" else State.WARN,
                summary=f"Reachable: {'Yes' if value == 'True' else 'No'}",
            )
        else:
            yield Result(state=State.OK, notice=f"{key}: {value}")


register.check_plugin(
    name="mshpc_node_status",
    service_name="MSHPC Node Status",
    discovery_function=discover_mshpc_node_status,
    check_function=check_mshpc_node_status,
    check_default_parameters={},
    # check_ruleset_name="mshpc_node_status",
)
