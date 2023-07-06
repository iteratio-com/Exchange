#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Mapping, Any
from .agent_based_api.v1 import register, Service, Result, State, check_levels, render, Metric
from .agent_based_api.v1.type_defs import CheckResult, DiscoveryResult, StringTable

MaxDBData = dict[str, Any]

def parse_maxdb_data(string_table: StringTable) -> MaxDBData:
    parsed, srv = {}, ""
    for line in string_table:
        if line[0] and line[0].strip() in ["OK", "END", "CONTINUE", "State"]:
            continue
        if line[0].startswith("[["):
            srv = line[0].replace("[[", "").replace("]]", "")
            parsed.setdefault(srv, {})
        elif len(line) == 2:
            key, value = line
            parsed[srv][key.strip()] = eval(value.strip())
    return parsed


register.agent_section(
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
    for item in section:
        yield Service(item=item)


def check_maxdb_user(item: str, params: Mapping[str, Any], section: MaxDBData) -> CheckResult:
    if item not in section:
        yield Result(state=State.UNKNOWN, summary=f"No Data for {item} found")
        return
    data = section.get(item)
    active_sessions = data.get("ACTIVE_SESSIONS", 0)
    max_user = data.get("MAXUSERS", 0)

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
        render_func=int,
        label="Current Active Sessions",
    )
    yield Result(state=State.OK, summary=f"Max User: {max_user}")


register.check_plugin(
    name="maxdb_user",
    sections=["maxdb_data"],
    service_name="MaxDB %s Sessions",
    check_ruleset_name="maxdb_sessions",
    check_default_parameters={"levels_perc": (80, 90)},
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
    if item not in section:
        yield Result(state=State.UNKNOWN, summary=f"No Data for {item} found")
        return
    data = section.get(item)
    used_log_pages_size = data.get("EXPRESSION1", 0)
    used_log_pages = data.get("USED_LOG_PAGES")
    log_pages_size = data.get("EXPRESSION2", 0)
    log_pages = data.get("LOG_PAGES", 0)
    log_state = data.get("LOGFULL", "")

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
        used_log_pages_size,
        metric_name="used_log_pages",
        levels_upper=None,
        render_func=int,
        label="Used Log Pages",
    )
    yield Metric("log_pages", log_pages)


register.check_plugin(
    name="maxdb_log",
    sections=["maxdb_data"],
    service_name="MaxDB %s Log",
    check_ruleset_name="maxdb_db_sizes_log",
    check_default_parameters={"levels_perc": (80, 90)},
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
    if item not in section:
        yield Result(state=State.UNKNOWN, summary=f"No Data for {item} found")
        return

    data = section.get(item)
    databasefull = data.get("DATABASEFULL")
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

    yield from check_levels(
        used_size * 1024,
        metric_name="used_size_bytes",
        levels_upper=params.get("levels_bytes"),
        render_func=render.bytes,
        label="Used Size",
    )

    yield Result(state=State.OK, summary=f"Total Size: {render.bytes(usable_size * 1024)}")
    yield Metric("usable_size_bytes", usable_size * 1024)

    yield Result(
        state=State(0 if data.get("BADINDEXES") == 0 else params.get("badindexes")),
        notice=f"Bad Indexes: {data.get('BADINDEXES')}",
    )
    yield Result(
        state=State(0 if data.get("BADVOLUMES") == 0 else params.get("badvolumes")),
        notice=f"Bad Volumes: {data.get('BADVOLUMES')}",
    )


register.check_plugin(
    name="maxdb_data",
    sections=["maxdb_data"],
    service_name="MaxDB %s Data",
    check_ruleset_name="maxdb_db_sizes",
    check_default_parameters={"levels_perc": (80, 90), "badindexes": 1, "badvolumes": 2},
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
    if item not in section:
        yield Result(state=State.UNKNOWN, summary=f"No Data for {item} found")
        return

    yield from check_levels(
        float(section.get(item, {}).get("DATACACHE_HITRATE", 0)),
        metric_name="datacache_hitrate",
        levels_upper=None,
        levels_lower=params.get("levels_lower"),
        render_func=render.percent,
        label="Data Cache Hitrate",
    )


register.check_plugin(
    name="maxdb_hitrate",
    sections=["maxdb_data"],
    service_name="MaxDB %s Cache Hitrate",
    check_ruleset_name="maxdb_hitrate",
    check_default_parameters={"levels_lower": (80, 90)},
    discovery_function=discover_maxdb,
    check_function=check_maxdb_hitrate,
)
