"""MaxDB Checkmk agent-based check plugin."""

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    State,
)
from cmk_addons.plugins.maxdb.lib.backup import check_backup
from cmk_addons.plugins.maxdb.lib.common import CheckParams, Section, discover_backup, parse_json


def discover(section: Section) -> DiscoveryResult:
    yield from discover_backup(section)


def check(item: str, params: CheckParams, section: Section) -> CheckResult:
    yield from check_backup(item, params, section, "LOG", "Log backup")
    auto = next((q for q in section[item].get("queries", []) if q.get("query") == "auto_log"), None)
    if not auto or auto.get("status") != "ok":
        yield Result(state=State.UNKNOWN, summary="Automatic log backup state unavailable")
        return
    value = auto.get("output", "").upper()
    if "AUTOSAVE IS OFF" in value:
        yield Result(state=State(params["auto_log_off"]), summary="Automatic log backup is OFF")
    elif "AUTOSAVE IS ON" in value:
        yield Result(state=State.OK, summary="Automatic log backup is ON")
    else:
        yield Result(state=State.UNKNOWN, summary="Automatic log backup state unknown")


agent_section_maxdb_backup_extended = AgentSection(
    name="maxdb_backup_extended", parse_function=parse_json
)
check_plugin_maxdb_log_backup = CheckPlugin(
    name="maxdb_log_backup",
    service_name="MaxDB %s Log Backup",
    sections=["maxdb_backup_extended"],
    discovery_function=discover,
    check_function=check,
    check_ruleset_name="maxdb_log_backup",
    check_default_parameters={
        "age": ("fixed", (86400.0, 172800.0)),
        "failed_state": 1,
        "auto_log_off": 1,
    },
)
