from time import time

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    GetRateError,
    Metric,
    Result,
    State,
    check_levels,
    get_rate,
    get_value_store,
)
from cmk_addons.plugins.maxdb.lib.common import (
    CheckParams,
    Section,
    discover_query,
    fields,
    number,
    parse_json,
)


def discover(section: Section) -> DiscoveryResult:
    yield from discover_query(section, "lock_statistics")


def check(item: str, params: CheckParams, section: Section) -> CheckResult:
    values = fields(section[item], "lock_statistics")
    if values is None:
        yield Result(state=State.UNKNOWN, summary="Lock statistics unavailable")
        return
    for key, label, setting in (
        ("USEDENTRYCOUNTPERCENTAGE", "Lock entries used", "lock_usage"),
        ("REQUESTORCOUNT", "Waiting lock requestors", "waiting"),
    ):
        value = number(values, key)
        if value is not None:
            yield from check_levels(
                value,
                levels_upper=params[setting],
                metric_name="maxdb_" + key.lower(),
                label=label,
                render_func=lambda v: f"{v:g}",
            )
    now = time()
    for key, label in (
        ("DEADLOCKCOUNT", "Deadlocks"),
        ("SQLLOCKCOLLISIONCOUNT", "SQL lock collisions"),
        ("SQLREQUESTTIMEOUTCOUNT", "SQL lock timeouts"),
    ):
        value = number(values, key)
        if value is None:
            continue
        yield Metric("maxdb_" + key.lower(), value)
        try:
            rate = get_rate(get_value_store(), f"maxdb_{item}_{key}", now, value)
        except (GetRateError, ValueError, ZeroDivisionError):
            yield Result(state=State.OK, summary=f"{label}: {value:g} total (rate pending)")
        else:
            yield Metric("maxdb_" + key.lower() + "_per_sec", rate)
            yield Result(state=State.OK, summary=f"{label}: {rate:.3f}/s")


agent_section_maxdb_locks = AgentSection(name="maxdb_locks", parse_function=parse_json)
check_plugin_maxdb_locks = CheckPlugin(
    name="maxdb_locks",
    service_name="MaxDB %s Locks",
    discovery_function=discover,
    check_function=check,
    check_ruleset_name="maxdb_locks",
    check_default_parameters={
        "lock_usage": ("fixed", (80.0, 90.0)),
        "waiting": ("fixed", (1.0, 5.0)),
    },
)
