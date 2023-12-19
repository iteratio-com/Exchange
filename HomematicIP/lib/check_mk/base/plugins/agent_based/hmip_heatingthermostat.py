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


def parse_homematicip_heatingthermostat(string_table: StringTable) -> HomematicIPSection:
    out = {}
    for (
        location,
        devicetype,
        devicelabel,
        statusdate,
        rssi,
        lowbattery,
        unreach,
        configpending,
        dutycycle,
        operationlock,
        valveposition,
        valvestate,
        temperatureoffset,
        setpointtemperature,
        valveactualtemperature,
    ) in string_table:
        out[location] = {
            "devicelabel": devicelabel,
            "devicetype": devicetype,
            "statusdate": statusdate,
            "rssi": int(rssi),
            "lowbattery": lowbattery,
            "unreach": unreach,
            "configpending": configpending,
            "dutycycle": dutycycle,
            "operationlock": operationlock,
            "valveposition": float(valveposition) * 100,
            "valvestate": valvestate,
            "temperatureoffset": float(temperatureoffset),
            "setpointtemperature": float(setpointtemperature),
            "valveactualtemperature": float(valveactualtemperature),
        }
    return out


def host_label_homematicip(section: HomematicIPSection) -> HostLabelGenerator:
    yield HostLabel("hmipNode", "yes")


register.agent_section(
    name="homematicip_heatingthermostat",
    parse_function=parse_homematicip_heatingthermostat,
    host_label_function=host_label_homematicip,
)

default_parameters = {
    "configpending": 1,
    "dutycycle": 1,
    "lowbattery": 2,
    "operationlock": 0,
    "rssi": (-85, -90),
    "setpointtemperature": {"lower": (15.0, 12.0), "upper": (26.0, 30.0)},
    "unreach": 2,
    "valveactualtemperature": {"lower": (15.0, 12.0), "upper": (26.0, 30.0)},
    "valvestate": 2,
}


def discover_homematicip_heatingthermostat(section: HomematicIPSection) -> DiscoveryResult:
    for item in section:
        yield Service(item=item, labels=[ServiceLabel("hmipHeatingThermostat", "yes")])


def check_homematicip_heatingthermostat(
    item: str, params: Mapping[str, Any], section: HomematicIPSection
) -> CheckResult:
    if (thermostate := section.get(item)) is None:
        return

    default_state = State.WARN

    yield Metric(
        name="valveposition",
        value=thermostate["valveposition"],
    )

    yield from check_levels(
        thermostate["valveactualtemperature"],
        levels_lower=params.get("valveactualtemperature", {}).get("lower"),
        levels_upper=params.get("valveactualtemperature", {}).get("upper"),
        metric_name="valveactualtemperature",
        label="Sensor temperature",
        render_func=lambda p: f"{p} °C",
    )

    yield from check_levels(
        thermostate["setpointtemperature"],
        levels_lower=params.get("setpointtemperature", {}).get("lower"),
        levels_upper=params.get("setpointtemperature", {}).get("upper"),
        metric_name="setpointtemperature",
        label="Set temperature",
        render_func=lambda p: f"{p} °C",
    )

    yield from check_levels(
        thermostate["rssi"],
        metric_name="rssi",
        levels_lower=params.get("rssi", ()),
        notice_only=True,
        label="RSSI Value",
    )

    yield Result(
        state=State.OK
        if thermostate["configpending"] == "False"
        else State(params.get("configpending", default_state)),
        notice=f"Config pending: {thermostate['configpending']}",
    )

    yield Result(
        state=State.OK
        if thermostate["dutycycle"] == "False"
        else State(params.get("dutycycle", default_state)),
        notice=f"Duty cycle: {thermostate['dutycycle']}",
    )

    yield Result(
        state=State.OK
        if thermostate["lowbattery"] == "False"
        else State(params.get("lowbattery", default_state)),
        notice=f"Low battery: {thermostate['lowbattery']}",
    )

    yield Result(
        state=State.OK
        if thermostate["operationlock"] == "False"
        else State(params.get("operationlock", default_state)),
        notice=f"Operation lock: {thermostate['operationlock']}",
    )

    yield Result(
        state=State.OK
        if thermostate["unreach"] == "False"
        else State(params.get("unreach", "STATE.CRIT")),
        notice=f"Unreach: {thermostate['unreach']}",
    )

    yield Result(
        state=State.OK
        if thermostate["valvestate"] == "ADAPTION_DONE"
        else State(params.get("valvestate", default_state)),
        notice=f"Valve state: {thermostate['valvestate']}",
    )


register.check_plugin(
    name="homematicip_heatingthermostat",
    service_name="Thermostat %s",
    discovery_function=discover_homematicip_heatingthermostat,
    check_default_parameters=default_parameters,
    check_function=check_homematicip_heatingthermostat,
    check_ruleset_name="homematicip_heatingthermostat",
)
