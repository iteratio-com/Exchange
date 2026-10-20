import json
import re
from collections.abc import Mapping
from typing import Any

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    IgnoreResultsError,
    Metric,
    Result,
    Service,
    State,
    StringTable,
    check_levels,
    render,
)

MaxDBData = dict[str, Any]


def parse_maxdb_data(string_table: StringTable) -> MaxDBData:
    """Accept JSON emitted by the new agent and legacy KEY=VALUE output.

    Legacy parsing is deliberately non-evaluating, so existing cached agent
    output can still be consumed during an upgrade.
    """
    parsed: MaxDBData = {}
    srv = ""
    for row in string_table:
        if not row:
            continue
        raw = " ".join(row).strip()
        if raw.startswith("{"):
            try:
                obj = json.loads(raw)
            except (json.JSONDecodeError, TypeError):
                continue
            if not isinstance(obj, dict):
                continue
            database, values = obj.get("database"), obj.get("values")
            if isinstance(database, str) and isinstance(values, dict):
                parsed[database] = values
            continue
        if row[0].startswith("[["):
            srv = row[0].removeprefix("[[").removesuffix("]]")
            parsed.setdefault(srv, {})
            continue
        if row[0].strip() in ("OK", "END", "CONTINUE", "State") or not srv:
            continue
        if len(row) == 2:
            key, value = row
        elif "=" in raw:
            key, value = raw.split("=", 1)
        else:
            continue
        key, value = key.strip(), value.strip().strip("\"'")
        if not re.fullmatch(r"[A-Z][A-Z0-9_]*", key):
            continue
        if re.fullmatch(r"[+-]?\d+", value):
            parsed[srv][key] = int(value)
        elif re.fullmatch(r"[+-]?(?:\d+\.\d*|\d*\.\d+)(?:[eE][+-]?\d+)?", value):
            parsed[srv][key] = float(value)
        else:
            parsed[srv][key] = value
    return parsed


agent_section_maxdb_data = AgentSection(
    name="maxdb_data",
    parse_function=parse_maxdb_data,
)

# User Sessions
#    ____                   _
#   / ___|   ___  ___  ___ (_)  ___   _ __   ___
#   \___ \  / _ \/ __|/ __|| | / _ \ | '_ \ / __|
#    ___) ||  __/\__ \\__ \| || (_) || | | |\__ \
#   |____/  \___||___/|___/|_| \___/ |_| |_||___/
#


def discover_maxdb(section: MaxDBData) -> DiscoveryResult:
    for srv in section:
        yield Service(item=srv)


def check_maxdb_user(item: str, params: Mapping[str, Any], section: MaxDBData) -> CheckResult:
    if not (data := section.get(item)):
        return

    active_sessions = data.get("ACTIVE_SESSIONS", 0)
    max_user = data.get("MAXUSERS", 0)

    if max_user == 0:
        raise IgnoreResultsError("Login to database failed")

    yield from check_levels(
        100.0 * active_sessions / max_user,
        metric_name="session_usage",
        levels_upper=params.get("levels_perc"),
        render_func=render.percent,
        label="Current Session Usage",
    )
    yield from check_levels(
        active_sessions,
        metric_name="active_sessions",
        levels_upper=params.get("levels_abs"),
        render_func=lambda x: str(int(x)),
        label="Current Active Sessions",
    )
    yield Result(state=State.OK, summary=f"Max User: {max_user}")


check_plugin_maxdb_user = CheckPlugin(
    name="maxdb_user",
    sections=["maxdb_data"],
    service_name="MaxDB %s Sessions",
    check_ruleset_name="maxdb_sessions",
    check_default_parameters={"levels_perc": ("fixed", (80, 90))},
    discovery_function=discover_maxdb,
    check_function=check_maxdb_user,
)

# Log
#    _        ___     ____
#   | |      / _ \   / ___|
#   | |     | | | | | |  _
#   | |___  | |_| | | |_| |
#   |_____|  \___/   \____|
#


def check_maxdb_log(item: str, params: Mapping[str, Any], section: MaxDBData) -> CheckResult:
    if not (data := section.get(item)):
        return

    used_log_pages_size = data.get("EXPRESSION1", 0)
    used_log_pages = data.get("USED_LOG_PAGES")
    log_pages_size = data.get("EXPRESSION2", 0)
    log_pages = data.get("LOG_PAGES", 0)
    log_state = data.get("LOGFULL", "")

    if log_pages_size == 0:
        raise IgnoreResultsError("Login to database failed")

    yield Result(
        state=State.OK if log_state == "No" else State.CRIT, notice=f"Log Full is {log_state}"
    )

    yield from check_levels(
        100.0 * used_log_pages_size / log_pages_size,
        metric_name="used_log_pages_perc",
        levels_upper=params.get("levels_perc"),
        render_func=render.percent,
        label="Log Usage",
    )
    yield from check_levels(
        used_log_pages_size * 1024,
        metric_name="used_log_pages_bytes",
        levels_upper=params.get("levels_bytes"),
        render_func=render.bytes,
        label="Used Log Size",
    )
    yield Result(state=State.OK, summary=f"Total Size: {render.bytes(log_pages_size * 1024)}")
    yield Metric("log_pages_bytes", log_pages_size * 1024)

    yield from check_levels(
        used_log_pages,
        metric_name="used_log_pages",
        render_func=lambda x: str(int(x)),
        label="Used Log Pages",
    )
    yield Metric("log_pages", log_pages)


check_plugin_maxdb_log = CheckPlugin(
    name="maxdb_log",
    sections=["maxdb_data"],
    service_name="MaxDB %s Log",
    check_ruleset_name="maxdb_db_sizes_log",
    check_default_parameters={"levels_perc": ("fixed", (80, 90))},
    discovery_function=discover_maxdb,
    check_function=check_maxdb_log,
)

# Data
#    ____          _
#   |  _ \   __ _ | |_  __ _
#   | | | | / _` || __|/ _` |
#   | |_| || (_| || |_| (_| |
#   |____/  \__,_| \__|\__,_|
#


def check_maxdb_data(item, params: Mapping[str, Any], section: MaxDBData) -> CheckResult:
    if not (data := section.get(item)):
        return

    databasefull = data.get("DATABASEFULL")
    if not isinstance(databasefull, str):
        raise IgnoreResultsError("Login to database failed")

    yield Result(
        state=State.OK if databasefull == "No" else State.CRIT,
        notice=f"Database is Full: {databasefull}",
    )

    usable_size = data.get("USABLESIZE")
    used_size = data.get("USEDSIZE")

    yield from check_levels(
        100.0 * used_size / usable_size,
        metric_name="database_usage_perc",
        levels_upper=params.get("levels_perc"),
        render_func=render.percent,
        label="Database Usage",
    )
    factor = 1024

    yield from check_levels(
        used_size * factor,
        metric_name="used_size_bytes",
        levels_upper=params.get("levels_bytes"),
        render_func=render.bytes,
        label="Used Size",
    )

    yield Result(state=State.OK, summary=f"Total Size: {render.bytes(usable_size * factor)}")
    yield Metric("usable_size_bytes", usable_size * factor)

    yield Result(
        state=State(0 if data.get("BADINDEXES") == 0 else params.get("badindexes")),
        notice=f"Bad Indexes: {data.get('BADINDEXES')}",
    )
    yield Result(
        state=State(0 if data.get("BADVOLUMES") == 0 else params.get("badvolumes")),
        notice=f"Bad Volumes: {data.get('BADVOLUMES')}",
    )


check_plugin_maxdb_data = CheckPlugin(
    name="maxdb_data",
    sections=["maxdb_data"],
    service_name="MaxDB %s Data",
    check_ruleset_name="maxdb_db_sizes",
    check_default_parameters={"levels_perc": ("fixed", (80, 90)), "badindexes": 1, "badvolumes": 2},
    discovery_function=discover_maxdb,
    check_function=check_maxdb_data,
)

#    _   _  _  _                _
#   | | | |(_)| |_  _ __  __ _ | |_  ___
#   | |_| || || __|| '__|/ _` || __|/ _ \
#   |  _  || || |_ | |  | (_| || |_|  __/
#   |_| |_||_| \__||_|   \__,_| \__|\___|
#


def check_maxdb_hitrate(
    item: str, params: Mapping[str, Any], section: Mapping[str, Any]
) -> CheckResult:
    if not (data := section.get(item)):
        return

    if data.get("DATACACHE_HITRATE") is None:
        raise IgnoreResultsError("Login to database failed")

    yield from check_levels(
        float(data.get("DATACACHE_HITRATE", 0)),
        metric_name="datacache_hitrate",
        levels_lower=params.get("levels_lower"),
        render_func=render.percent,
        label="Data Cache Hitrate",
    )


check_plugin_maxdb_hitrate = CheckPlugin(
    name="maxdb_hitrate",
    sections=["maxdb_data"],
    service_name="MaxDB %s Cache Hitrate",
    check_ruleset_name="maxdb_hitrate",
    check_default_parameters={"levels_lower": ("fixed", (80, 90))},
    discovery_function=discover_maxdb,
    check_function=check_maxdb_hitrate,
)
