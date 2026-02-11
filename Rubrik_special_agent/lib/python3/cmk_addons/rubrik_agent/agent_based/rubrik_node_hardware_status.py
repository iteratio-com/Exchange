#!/usr/bin/env python3

from collections.abc import Mapping
from typing import Any

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    State,
    StringTable,
)

from .utils.rubrik_api import RubrikSection


def parse_rubrik_node_hardware_health(string_table: StringTable) -> RubrikSection:
    out = {}
    title = ""
    last_key = {"SSD Life-Left": False}
    for table_line in string_table:
        line = table_line[0]
        if len(line.split(":")) == 2 and line.split(":")[1]:  # noqa: PLR2004
            key, value = line.split(":")
            if value:
                out[key.strip()] = value.strip()
            continue
        if line.startswith("Checking ") and line.endswith("for errors."):
            title = line.split()[1] + "_errors"
            out.setdefault(title, [])
            last_key["SSD Life-Left"] = False
            continue
        if line.startswith("FRU Replacement Summary:"):
            title = "FRU"
            out.setdefault(title, [])
            last_key["SSD Life-Left"] = False
            continue
        if line.startswith("-----"):
            title = ""
            last_key["SSD Life-Left"] = False
            continue
        if line.startswith("Disk Device") and line.endswith("SSD Life-Left"):
            title = "SSD Life-Left"
            out.setdefault(title, [])
            last_key["SSD Life-Left"] = True
            continue
        if line.startswith("/dev/sd") and last_key["SSD Life-Left"]:
            device = line.split("|")[0].strip()
            percentage = line.split("|")[-1].strip()
            out[title].append((device, percentage.replace("%", "").strip()))
            continue
        if title:
            out[title].append(line.strip())

        last_key["SSD Life-Left"] = False

    return out


agent_section_rubrik_node_hardware_health = AgentSection(
    name="rubrik_node_hardware_health",
    parse_function=parse_rubrik_node_hardware_health,
)


def discover_node_hardware_health(section: RubrikSection) -> DiscoveryResult:
    if section:
        yield Service()


def check_node_hardware_health(params: Mapping[str, Any], section: RubrikSection) -> CheckResult:  # noqa: ARG001
    if not section:
        return

    if fru := section.get("FRU", []):
        if "All FRUS in the node are healthy." in fru[0]:
            yield Result(
                state=State.OK,
                summary="All FRUS in the node are healthy",
            )
        else:
            yield Result(
                state=State.CRIT,
                summary=f"FRU in the node are not healthy {', '.join(fru)}",
            )

    defect_disks = {"ok": [], "errors": []}

    for partition in section:
        if partition.startswith("sd") and partition.endswith("_errors"):
            if len(section[partition]) != 0:
                defect_disks["errors"].append(
                    f"Errors on {partition.replace('_errors', '')}: {', '.join(section[partition])}",
                )
            else:
                defect_disks["ok"].append(partition)

    yield Result(
        state=State.CRIT if defect_disks["errors"] else State.OK,
        details=(f"Defect disks: {', '.join(defect_disks['errors'])}" if defect_disks["errors"] else "No defect disks"),
        summary=(
            f"{len(defect_disks['ok'])} disks are okay"
            if not defect_disks["errors"]
            else "see errors of disks in details"
        ),
    )


check_plugin_rubrik_node_hardware_health = CheckPlugin(
    name="rubrik_node_hardware_health",
    service_name="Rubrik Node Hardware Health",
    discovery_function=discover_node_hardware_health,
    check_function=check_node_hardware_health,
    check_ruleset_name="rubrik_node_hardware_status",
    check_default_parameters={
        "percent_ssd_life_left": (50, 10),
    },
)
