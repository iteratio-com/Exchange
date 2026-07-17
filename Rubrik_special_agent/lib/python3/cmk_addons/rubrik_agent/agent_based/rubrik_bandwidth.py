#!/usr/bin/env python3

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    State,
    check_levels,
    render,
)

from .utils.rubrik_api import RubrikSection, parse_rubrik_single


agent_section_rubrik_bandwidth = AgentSection(
    name="rubrik_bandwidth",
    parse_function=parse_rubrik_single,
)


def discover_rubrik_bandwidth(section: RubrikSection) -> DiscoveryResult:
    if section:
        yield Service()


def check_rubrik_bandwidth(section: RubrikSection) -> CheckResult:
    if not section:
        return

    avg_bytes_per_second = section.get("archiveAvgBytesPerSecondLastHour")
    if avg_bytes_per_second is None:
        yield Result(state=State.UNKNOWN, summary="Missing data")
        return

    yield from check_levels(
        int(avg_bytes_per_second),
        label="Average bandwidth",
        metric_name="rubrik_bandwidth",
        render_func=render.iobandwidth,
    )


check_plugin_rubrik_bandwidth = CheckPlugin(
    name="rubrik_bandwidth",
    service_name="Rubrik Cluster Bandwidth",
    discovery_function=discover_rubrik_bandwidth,
    check_function=check_rubrik_bandwidth,
)
