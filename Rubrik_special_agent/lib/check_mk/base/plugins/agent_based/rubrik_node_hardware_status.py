#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# 2023, marcus.klein@iteratio.com

from .agent_based_api.v1 import Result, Service, State, register
from .agent_based_api.v1.type_defs import CheckResult, DiscoveryResult, StringTable
from .utils.rubrik_api import RubrikSection


def parse_rubrik_node_hardware_health(string_table: StringTable) -> RubrikSection:
    out = {}
    title = ""
    for line in string_table:
        line = line[0]
        if len(line.split(":")) == 2 and line.split(":")[1]:
            key, value = line.split(":")
            if value:
                out[key.strip()] = value.strip()
            continue
        if line.startswith("Checking ") and line.endswith("for errors."):
            title = line.split()[1] + "_errors"
            out.setdefault(title, [])
            continue
        if line.startswith("FRU Replacement Summary:"):
            title = "FRU"
            out.setdefault(title, [])
            continue

        if line.startswith("-----"):
            title = ""
            continue
        if title:
            out[title].append(line.strip())

    return out


register.agent_section(
    name="rubrik_node_hardware_health",
    parse_function=parse_rubrik_node_hardware_health,
)


def discover_node_hardware_health(section: RubrikSection) -> DiscoveryResult:
    if section:
        yield Service()


def check_node_hardware_health(section: RubrikSection) -> CheckResult:
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
        details=f"Defect disks: {', '.join(defect_disks['errors'])}"
        if defect_disks["errors"]
        else "No defect disks",
        summary=f"{len(defect_disks['ok'])} disks are okay"
        if not defect_disks["errors"]
        else "see errors of disks in details",
    )


register.check_plugin(
    name="rubrik_node_hardware_health",
    service_name="Rubrik Node Hardware Health",
    discovery_function=discover_node_hardware_health,
    check_function=check_node_hardware_health,
)
