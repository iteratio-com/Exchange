#!/usr/bin/env python3

from typing import Any

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    State,
    check_levels,
)

from .utils.rubrik_api import RubrikSection, parse_rubrik_single


agent_section_rubrik_storage = AgentSection(
    name="rubrik_storage",
    parse_function=parse_rubrik_single,
)


def discover_rubrik_storage(section: RubrikSection) -> DiscoveryResult:
    if section:
        yield Service()


def check_rubrik_storage(section: RubrikSection) -> CheckResult:
    if not section:
        return

    runway_remaining = section.get("runwayRemaining")
    if runway_remaining is None:
        yield Result(state=State.UNKNOWN, summary="Missing data")
        return

    yield from check_levels(
        int(runway_remaining),
        label="Runway remaining",
        metric_name="rubrik_storage_runway_remaining",
        levels_lower=("fixed", (30, 14)),
        render_func=lambda value: f"{int(value)} days",
    )


check_plugin_rubrik_storage = CheckPlugin(
    name="rubrik_storage",
    service_name="Rubrik Cluster Storage",
    discovery_function=discover_rubrik_storage,
    check_function=check_rubrik_storage,
)
