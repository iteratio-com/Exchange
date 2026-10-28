from collections.abc import Mapping
from typing import Any

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    HostLabel,
    HostLabelGenerator,
    InventoryPlugin,
    InventoryResult,
    Result,
    Service,
    State,
    StringTable,
    TableRow,
)

MaxDBData = dict[str, Any]
MaxDBState = dict[str, Any]


def parse_maxdb_state(string_table: StringTable) -> MaxDBState:
    parsed, srv, installation = {}, "", ""
    for line in string_table:
        if line[0] and line[0].strip() in ["OK", "END", "CONTINUE", "State"]:
            continue
        if line[0].startswith("[["):
            srv = line[0].replace("[[", "").replace("]]", "")
            parsed.setdefault(srv, {})
        elif len(line) == 1:
            parsed[srv]["state"] = line[0].lower()
        elif line[0].startswith("Installation:"):
            installation = " ".join(line[1:])
            parsed[srv].setdefault(installation, {})
        elif len(line) > 3:
            if line[-1].lower() == "bit":
                package = " ".join(line[:-4])
                parsed[srv][installation].setdefault(package, {})
                parsed[srv][installation][package] = {
                    "version": line[-4],
                    "validation": line[-3],
                    "binary": "".join(line[-2:]),
                }
            else:
                if "MSG" in line:
                    line.remove("MSG")
                package = " ".join(line[:-2])
                parsed[srv][installation].setdefault(package, {})
                parsed[srv][installation][package] = {
                    "version": line[-2],
                    "validation": line[-1],
                }
    return parsed


def maxdb_host_labels(section: MaxDBState) -> HostLabelGenerator:
    if section:
        yield HostLabel("cmk/maxdb", "yes")


agent_section_maxdb_state = AgentSection(
    name="maxdb_state",
    parse_function=parse_maxdb_state,
    host_label_function=maxdb_host_labels,
)


def discover_maxdb_state(
    section_maxdb_state: MaxDBState | None, section_maxdb_data: MaxDBData | None
) -> DiscoveryResult:
    for item in section_maxdb_state:
        yield Service(item=item)


def check_maxdb_state(
    item: str,
    params: Mapping[str, Any],
    section_maxdb_state: MaxDBState | None,
    section_maxdb_data: MaxDBData | None,
) -> CheckResult:
    if not (data := section_maxdb_state.get(item)):
        return

    status_map = {
        "offline": State.CRIT,
        "cold": State.WARN,
        "admin": State.WARN,
        "online": State.OK,
    }
    yield Result(
        state=status_map.get(data.get("state"), State.UNKNOWN),
        summary=f"Database status is: {data.get('state', '').title()}",
    )
    for key, values in data.items():
        if key.startswith(item):
            if base := values.get("Base"):
                yield Result(
                    state=State.OK,
                    summary=f"Running Version: {base.get('version', '')} ({base.get('validation', '')}, {base.get('binary', '')})",
                )

    if section_maxdb_data:
        maxdb_data = section_maxdb_data.get(item)
        yield Result(
            state=State(
                0
                if maxdb_data.get("AUTOSAVESTANDBY", "not set").lower() == "on"
                else params.get("autosave", 0)
            ),
            summary=f"Auto Save Standby: {maxdb_data.get('AUTOSAVESTANDBY', 'not set')}",
        )
    else:
        yield Result(
            state=State.OK,
            summary="No Auto Save Standby aviaviable, please 'data' to Plugin execution",
        )


check_plugin_maxdb_state = CheckPlugin(
    name="maxdb_state",
    sections=["maxdb_state", "maxdb_data"],
    service_name="MaxDB %s Info",
    discovery_function=discover_maxdb_state,
    check_ruleset_name="maxdb_db_config",
    check_default_parameters={"autosave": 0},
    check_function=check_maxdb_state,
)


def inventory_maxdb_software(section: MaxDBState) -> InventoryResult:
    path = ["software", "applications", "sapmaxdb"]
    for db, installtions in section.items():
        for installation, package in installtions.items():
            if installation == "state":
                continue
            for item, values in package.items():
                add_path = installation.replace(" ", "").replace("/", "").replace(db, "").lower()
                yield TableRow(
                    path=path + [add_path],
                    key_columns={"name": item},
                    inventory_columns={
                        "version": values.get("version", ""),
                        "validation": values.get("validation", ""),
                        "binary": values.get("binary", ""),
                    },
                )


inventory_plugin_inventory_maxdb_software = InventoryPlugin(
    name="inventory_maxdb_software",
    sections=["maxdb_state"],
    inventory_function=inventory_maxdb_software,
)
