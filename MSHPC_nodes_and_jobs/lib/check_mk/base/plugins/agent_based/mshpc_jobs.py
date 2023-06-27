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


def parse_mshpc_jobs(string_table):
    try:
        data = eval("".join([i[0] for i in string_table]))
    except:
        data = {}
    return data


register.agent_section(
    name="mshpc_jobs",
    parse_function=parse_mshpc_jobs,
)


def discover_mshpc_jobs(section):
    if section:
        yield Service()


def check_mshpc_jobs(params, section):
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data from host")
        return

    jobs_total = 0

    for key, value in section.get("State", {}).items():
        levels = params.get(f"jobs_{key.lower()}", {})
        jobs_total += value
        yield from check_levels(
            value,
            levels_upper=levels.get("upper"),
            levels_lower=levels.get("lower"),
            metric_name=f"mshpc_jobs_state_{key.lower()}",
            render_func=int,
            label=key,
        )

    yield Metric("MSHPC_Jobs_Total", jobs_total)
    yield Result(state=State.OK, summary=f"Jobs total: {jobs_total}")


register.check_plugin(
    name="mshpc_jobs",
    service_name="MSHPC Jobs",
    discovery_function=discover_mshpc_jobs,
    check_function=check_mshpc_jobs,
    check_default_parameters={},
    check_ruleset_name="mshpc_jobs",
)
