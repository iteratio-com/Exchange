#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Any
from collections.abc import Mapping

from cmk.agent_based.v2 import (
    Service,
    Result,
    State,
    CheckPlugin,
    startswith,
    SNMPSection,
    StringTable,
    DiscoveryResult,
    CheckResult,
    SNMPTree,
)


DAMOCLES2_SECTION = dict[str, dict[str, Any]]


def parse_damocles2_inputs_outputs(string_table: StringTable) -> DAMOCLES2_SECTION:
    parsed = {"IN": {}, "OUT": {}}
    input_values, output_values = string_table

    for value, name, setup, state, inpcounter in input_values:
        parsed["IN"][name] = {
            "inpValue": value,
            "inpAlarmSetup": setup,
            "inpAlarmState": state,
            "inpCounter": inpcounter,
        }

    for value, name, device_type, mode, init in output_values:
        parsed["OUT"][name] = {
            "outValue": value,
            "outType": device_type,
            "outMode": mode,
            "outInit": init,
        }
    return parsed


snmp_section_damocles2_inputs_outputs = SNMPSection(
    name="damocles2_inputs_outputs",
    parse_function=parse_damocles2_inputs_outputs,
    fetch=[
        SNMPTree(
            base=".1.3.6.1.4.1.21796.3.4.1.1",
            oids=[
                "2",  # outValue
                "3",  # Name
                "4",  # AlarmSetup
                "5",  # AlarmState
                "6",  # inpCounter
            ],
        ),
        SNMPTree(
            base=".1.3.6.1.4.1.21796.3.4.2.1",
            oids=[
                "2",  # outValue
                "3",  # Name
                "4",  # type
                "5",  # Mode
                "6",  # outInit
            ],
        ),
    ],
    detect=startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.21796.3.4"),
)


def discover_damocles2_inputs(section: DAMOCLES2_SECTION) -> DiscoveryResult:
    for dev in section["IN"]:
        yield Service(item=dev)


def check_damocles2_inputs(
    item: str, params: Mapping[str, Any], section: DAMOCLES2_SECTION
) -> CheckResult:
    if not (sensor := section["IN"].get(item)):
        return

    yield Result(state=State.OK, summary="On" if sensor.get("inpValue") == "1" else "Off")

    setup_map = {
        "0": "inactive",
        "2": "activeOff",
        "1": "activeOn",
    }
    yield Result(
        state=State.OK,
        summary=f"Alarm Setup is {setup_map.get(sensor.get('inpAlarmSetup'),'unknown')}",
    )
    yield Result(
        state=State.OK if sensor.get("inpAlarmState") == "0" else State(params["alert_state"]),
        summary=f"State is {'normal' if sensor.get('inpAlarmState') == '0' else 'alarm'}",
    )


check_plugin_damocles2_inputs = CheckPlugin(
    name="damocles2_inputs",
    sections=["damocles2_inputs_outputs"],
    service_name="Input %s",
    discovery_function=discover_damocles2_inputs,
    check_default_parameters={"alert_state": 2},
    check_ruleset_name="damocles2_inputs_group",
    check_function=check_damocles2_inputs,
)


def discover_damocles2_outputs(section: DAMOCLES2_SECTION) -> DiscoveryResult:
    for dev in section["OUT"]:
        yield Service(item=dev)


def check_damocles2_outputs(item: str, section: DAMOCLES2_SECTION) -> CheckResult:
    if not (sensor := section["OUT"].get(item)):
        return

    yield Result(state=State.OK, summary=f"{'On' if sensor.get('inpValue') == '1' else 'Off'}")
    out_type_map = {
        "0": "OnOff",
        "2": "RTS",
        "1": "DTR",
    }
    yield Result(
        state=State.OK, summary=f"Output Type: {out_type_map.get(sensor.get('outType'),'Unknown')}"
    )

    out_mode_map = {
        "0": "manual",
        "1": "autoAlarm",
        "2": "autoTriggerEq",
        "3": "autoTriggerHi",
        "4": "autoTriggerLo",
    }
    yield Result(
        state=State.OK, summary=f"Output Mode: {out_mode_map.get(sensor.get('outMode'),'Unkown')}"
    )


check_plugin_damocles2_outputs = CheckPlugin(
    name="damocles2_outputs",
    sections=["damocles2_inputs_outputs"],
    service_name="Output %s",
    discovery_function=discover_damocles2_outputs,
    check_function=check_damocles2_outputs,
)
