#!/usr/bin/env python3

# 2023, marcus.klein@iteratio.com

from typing import Any, Mapping

from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    HostLabel,
    Metric,
    Result,
    Service,
    ServiceLabel,
    State,
    check_levels,
    register,
)
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import (
    CheckResult,
    DiscoveryResult,
    HostLabelGenerator,
    StringTable,
)

HomematicIPSection = dict[str, Any]


def parse_homematicip_shuttercontactmagnetic(string_table: StringTable) -> HomematicIPSection:
    out = {}
    for (
        location,
        devicetype,
        devicelabel,
        statusdate,
        rssi,
        windowstate,
    ) in string_table:
        out[location] = {
            "devicelabel": devicelabel,
            "devicetype": devicetype,
            "statusdate": statusdate,
            "rssi": int(rssi),
            "windowstate": windowstate,
        }
    return out


def host_label_homematicip(section: HomematicIPSection) -> HostLabelGenerator:
    yield HostLabel("hmipNode", "yes")


register.agent_section(
    name="homematicip_shuttercontactmagnetic",
    parse_function=parse_homematicip_shuttercontactmagnetic,
    host_label_function=host_label_homematicip,
)

default_parameters = {
    "windowstate_mon_state": 2,
    "windowstate": "CLOSED",
    "rssi": (-85, -90),
}


def discover_homematicip_shuttercontactmagnetic(section: HomematicIPSection) -> DiscoveryResult:
    for item in section:
        yield Service(item=item, labels=[ServiceLabel("hmipShutterContactMagnetic", "yes")])


def check_homematicip_shuttercontactmagnetic(
    item: str, params: Mapping[str, Any], section: HomematicIPSection
) -> CheckResult:
    if (shutter := section.get(item)) is None:
        return

    yield from check_levels(
        shutter["rssi"],
        metric_name="rssi",
        levels_lower=params.get("rssi", ()),
        notice_only=True,
        label="RSSI Value",
    )

    yield Result(
        state=State.OK
        if shutter["windowstate"] == params.get("windowstate", "CLOSED")
        else State(params.get("windowstate_mon_state", State.WARN)),
        summary=f"Window state: {shutter['windowstate'].capitalize()}",
    )


register.check_plugin(
    name="homematicip_shuttercontactmagnetic",
    service_name="Shutter Contact %s",
    discovery_function=discover_homematicip_shuttercontactmagnetic,
    check_default_parameters=default_parameters,
    check_function=check_homematicip_shuttercontactmagnetic,
    check_ruleset_name="homematicip_shuttercontactmagnetic",
)
