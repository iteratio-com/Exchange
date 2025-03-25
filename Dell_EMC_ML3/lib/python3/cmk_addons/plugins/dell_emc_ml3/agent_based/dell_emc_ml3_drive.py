#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Any
from collections.abc import Mapping

from cmk.agent_based.v2 import (
    Service,
    Result,
    exists,
    State,
    CheckPlugin,
    SimpleSNMPSection,
    StringTable,
    DiscoveryResult,
    CheckResult,
    SNMPTree,
    check_levels,
    render,
)


from dataclasses import dataclass


@dataclass
class TapeDrive:
    name: str
    ava: str
    cleaning: str
    power_on_hours: str
    op_status: str


DELL_SECTION = dict[str, TapeDrive]


def parse_dell_emc_ml3_drive(string_table: StringTable) -> DELL_SECTION:
    parsed = {}
    for index, name, ava, cleaning, power_on_hours, op_status in string_table:
        parsed[index] = TapeDrive(name, ava, cleaning, power_on_hours, op_status)
    return parsed


def discover_tape_drive(section: DELL_SECTION) -> DiscoveryResult:
    for tape_drive in section:
        yield Service(item=tape_drive)


def check_dell_emc_ml3_drive(item: str, params: Mapping[str, Any], section) -> CheckResult:
    if not (drive := section.get(item)):
        return

    yield Result(state=State.OK, summary=drive.name)

    ava_map = {
        "1": (State.WARN, "other"),
        "2": (State.UNKNOWN, "unknown"),
        "3": (State.OK, "runningFullPower"),
        "4": (State.WARN, "warning"),
        "5": (State.WARN, "inTest"),
        "6": (State.WARN, "notApplicable"),
        "7": (State.WARN, "powerOff"),
        "8": (State.WARN, "offLine"),
        "9": (State.WARN, "offDuty"),
        "10": (State.CRIT, "degraded"),
        "11": (State.WARN, "notInstalled"),
        "12": (State.CRIT, "installError"),
        "13": (State.WARN, "powerSaveUnknown"),
        "14": (State.WARN, "powerSaveLowPowerMode"),
        "15": (State.WARN, "powerSaveStandby"),
        "16": (State.WARN, "powerCycle"),
        "17": (State.WARN, "powerSaveWarning"),
        "18": (State.WARN, "paused"),
        "19": (State.WARN, "notReady"),
        "20": (State.WARN, "notConfigured"),
        "21": (State.WARN, "quiesced"),
    }
    status, txt = ava_map.get(drive.ava, (State.UNKNOWN, "unknown Status Code"))
    if params.get("ava_map"):
        status = params["ava_map"].get(f"ava_map_{drive.ava}")
        status = State(status)

    yield Result(state=status, summary=f"availability State: {txt}")

    cleaning_map = {
        "1": (params.get("cleaning_needed", State.WARN), "cleaning needed"),
        "2": (State.OK, "no cleaning needed"),
    }
    status, txt = cleaning_map.get(drive.cleaning, (State.UNKNOWN, "unknown Status"))
    yield Result(state=status, summary=f"Cleaning Status: {txt}")

    if drive.power_on_hours:
        yield from check_levels(
            int(drive.power_on_hours) * 3600,
            metric_name="uptime",
            render_func=render.timespan,
            label="Uptime",
        )

    op_status_map = {
        "0": (State.UNKNOWN, "unknown"),
        "1": (State.WARN, "other"),
        "2": (State.OK, "ok"),
        "3": (State.WARN, "degraded"),
        "4": (State.WARN, "stressed"),
        "5": (State.WARN, "predictiveFailure"),
        "6": (State.CRIT, "error"),
        "7": (State.CRIT, "non-RecoverableError"),
        "8": (State.WARN, "starting"),
        "9": (State.WARN, "stopping"),
        "10": (State.WARN, "stopped"),
        "11": (State.WARN, "inService"),
        "12": (State.WARN, "noContact"),
        "13": (State.CRIT, "lostCommunication"),
        "14": (State.WARN, "aborted"),
        "15": (State.WARN, "dormant"),
        "16": (State.CRIT, "supportingEntityInError"),
        "17": (State.OK, "completed"),
        "18": (State.WARN, "powerMode"),
        "19": (State.WARN, "dMTFReserved"),
    }
    status, txt = op_status_map.get(drive.op_status, (State.UNKNOWN, "unknown status"))
    if params.get("opa_map"):
        status = params["opa_map"].get(f"opa_map_{drive.op_status}", status)
        status = State(status)
    yield Result(state=status, summary=f"Operational Status: {txt}")


snmp_section_dell_emc_ml3_drive = SimpleSNMPSection(
    name="dell_emc_ml3_drive",
    detect=exists(".1.3.6.1.4.1.14851.3.1.6.2.1.*"),
    parse_function=parse_dell_emc_ml3_drive,
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.14851.3.1.6.2.1",
        oids=[
            "1",
            "3",
            "5",
            "6",
            "10",
            "11",
        ],
    ),
)

check_plugin_dell_emc_ml3_drive = CheckPlugin(
    name="dell_emc_ml3_drive",
    service_name="Tape Drive %s",
    discovery_function=discover_tape_drive,
    check_function=check_dell_emc_ml3_drive,
    check_ruleset_name="dell_emc_ml3_drive",
    check_default_parameters={},
)
