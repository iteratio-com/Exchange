#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# 2023, marcus.klein@iteratio.com

from typing import Any, Mapping

from .agent_based_api.v1 import Metric, Result, Service, State, check_levels, register, render
from .agent_based_api.v1.type_defs import CheckResult, DiscoveryResult
from .utils.rubrik_api import RubrikSection, parse_rubrik

register.agent_section(
    name="rubrik_cluster_compliance_24_hours",
    parse_function=parse_rubrik,
)


def discover_rubrik_cluster_compliance_24_hours(
    section: RubrikSection,
) -> DiscoveryResult:
    if section:
        yield Service()


def check_rubrik_cluster_compliance_24_hours(
    params: Mapping[str, Any], section: RubrikSection
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

    yield from check_levels(
        section["numberOfOutOfComplianceSnapshots"],
        metric_name="snapshots_out_of_compliance",
        levels_upper=params["absolute_out_of_compliance"],
        render_func=int,
        label="Snapshots out of compliance",
    )

    yield from check_levels(
        section["percentOutOfCompliance"],
        metric_name="snapshots_out_of_compliance_percent",
        levels_upper=params["percent_out_of_compliance"],
        render_func=render.percent,
        label="Percent snapshots out of compliance",
    )


register.check_plugin(
    name="rubrik_cluster_compliance_24_hours",
    service_name="Rubrik Compliance 24 Hours",
    discovery_function=discover_rubrik_cluster_compliance_24_hours,
    check_function=check_rubrik_cluster_compliance_24_hours,
    check_ruleset_name="rubrik_cluster_compliance_24_hours",
    check_default_parameters={
        "absolute_out_of_compliance": (1, 5),
        "percent_out_of_compliance": (1, 5),
    },
)
