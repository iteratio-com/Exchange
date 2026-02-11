#!/usr/bin/env python3

from collections.abc import Mapping
from typing import Any

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Metric,
    Result,
    Service,
    State,
    check_levels,
    render,
)

from .utils.rubrik_api import RubrikSection, parse_rubrik


def discover_rubrik_cluster_compliance_24_hours(
    section: RubrikSection,
) -> DiscoveryResult:
    if section:
        yield Service()


def check_rubrik_cluster_compliance_24_hours(
    params: Mapping[str, Any],
    section: RubrikSection,
) -> CheckResult:
    if not section:
        return

    yield Result(
        state=State.OK,
        summary=f"Total protected objects: {section['totalProtected']}, Snapshots awaiting first full: {section['numberAwaitingFirstFull']}",
    )

    yield Metric(
        name="total_protected_objects",
        value=section["totalProtected"],
    )

    yield Metric(
        name="snapshots_awaiting_first_full",
        value=section["numberAwaitingFirstFull"],
    )

    yield Metric(
        name="snapshots_in_compliance",
        value=section["numberOfInComplianceSnapshots"],
    )

    yield Metric(
        name="snapshots_in_compliance_percent",
        value=section["percentInCompliance"],
    )

    # Check absolute out of compliance levels
    abs_warn = params.get("absolute_out_of_compliance_warn")
    abs_crit = params.get("absolute_out_of_compliance_crit")
    if abs_warn is not None and abs_crit is not None:
        yield from check_levels(
            section["numberOfOutOfComplianceSnapshots"],
            metric_name="snapshots_out_of_compliance",
            levels_upper=("fixed", (abs_warn, abs_crit)),
            render_func=lambda x: str(int(x)),
            label="Snapshots out of compliance",
        )
    else:
        yield Metric(
            name="snapshots_out_of_compliance",
            value=section["numberOfOutOfComplianceSnapshots"],
        )

    # Check percentage out of compliance levels
    pct_warn = params.get("percent_out_of_compliance_warn")
    pct_crit = params.get("percent_out_of_compliance_crit")
    if pct_warn is not None and pct_crit is not None:
        yield from check_levels(
            section["percentOutOfCompliance"],
            metric_name="snapshots_out_of_compliance_percent",
            levels_upper=("fixed", (pct_warn, pct_crit)),
            render_func=render.percent,
            label="Percent snapshots out of compliance",
        )
    else:
        yield Metric(
            name="snapshots_out_of_compliance_percent",
            value=section["percentOutOfCompliance"],
        )


agent_section_rubrik_cluster_compliance_24_hours = AgentSection(
    name="rubrik_cluster_compliance_24_hours",
    parse_function=parse_rubrik,
)

check_plugin_rubrik_cluster_compliance_24_hours = CheckPlugin(
    name="rubrik_cluster_compliance_24_hours",
    service_name="Rubrik Compliance 24 Hours",
    discovery_function=discover_rubrik_cluster_compliance_24_hours,
    check_function=check_rubrik_cluster_compliance_24_hours,
    check_ruleset_name="rubrik_cluster_compliance_24_hours",
    check_default_parameters={
        "absolute_out_of_compliance_warn": 1,
        "absolute_out_of_compliance_crit": 5,
        "percent_out_of_compliance_warn": 1,
        "percent_out_of_compliance_crit": 5,
    },
)
