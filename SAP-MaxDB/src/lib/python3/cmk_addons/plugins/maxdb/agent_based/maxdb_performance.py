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
    yield from discover_query(section, "command_statistics")


def check(item: str, params: CheckParams, section: Section) -> CheckResult:
    command = fields(section[item], "command_statistics")
    if command is None:
        yield Result(state=State.UNKNOWN, summary="SQL command statistics unavailable")
        return
    command_id = command.get("COMMANDID", "unknown")
    yield Result(state=State.OK, summary=f"Command sample {command_id} (not database-wide)")
    now = time()
    for key, metric, label, setting in (
        ("EXECUTECOUNT", "maxdb_sql_executes_per_sec", "Executes", None),
        ("PREPARECOUNT", "maxdb_sql_prepares_per_sec", "Prepares", None),
        ("READROWCOUNT", "maxdb_sql_rows_read_per_sec", "Rows read", None),
        ("QUALIFIEDROWCOUNT", "maxdb_sql_rows_qualified_per_sec", "Rows qualified", None),
        (
            "PHYSICALREADCOUNT",
            "maxdb_sql_physical_reads_per_sec",
            "Physical reads",
            "physical_reads",
        ),
        ("VIRTUALREADCOUNT", "maxdb_sql_virtual_reads_per_sec", "Virtual reads", None),
        ("WAITCOUNT", "maxdb_sql_waits_per_sec", "Waits", "waits"),
        ("FETCHCOUNT", "maxdb_sql_fetches_per_sec", "Fetches", None),
    ):
        value = number(command, key)
        if value is None:
            continue
        try:
            rate = get_rate(get_value_store(), f"maxdb_sql_{item}_{command_id}_{key}", now, value)
        except (GetRateError, ValueError, ZeroDivisionError):
            continue
        if setting:
            yield from check_levels(
                rate,
                levels_upper=params[setting],
                metric_name=metric,
                label=label,
                render_func=lambda v: f"{v:.2f}/s",
            )
        else:
            yield Metric(metric, rate)
            yield Result(state=State.OK, summary=f"{label}: {rate:.2f}/s")
    for key, label in (
        ("AVGEXECUTETIME", "Average SQL execution time (raw MaxDB units)"),
        ("MAXEXECUTETIME", "Maximum SQL execution time (raw MaxDB units)"),
        ("CURRENTEXECUTECOUNT", "Currently executing"),
    ):
        value = number(command, key)
        if value is not None:
            yield Metric("maxdb_sql_" + key.lower(), value)
            yield Result(state=State.OK, summary=f"{label}: {value:g}")


agent_section_maxdb_performance = AgentSection(name="maxdb_performance", parse_function=parse_json)
check_plugin_maxdb_performance = CheckPlugin(
    name="maxdb_performance",
    service_name="MaxDB %s Performance",
    discovery_function=discover,
    check_function=check,
    check_ruleset_name="maxdb_performance",
    check_default_parameters={
        "waits": ("fixed", (10.0, 50.0)),
        "physical_reads": ("fixed", (1000.0, 5000.0)),
    },
)
