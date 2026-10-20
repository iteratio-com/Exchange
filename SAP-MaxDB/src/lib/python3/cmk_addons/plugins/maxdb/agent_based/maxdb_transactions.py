from datetime import datetime

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    State,
    check_levels,
    render,
)
from cmk_addons.plugins.maxdb.lib.common import (
    CheckParams,
    Section,
    discover_query,
    fields,
    parse_json,
)


def discover(section: Section) -> DiscoveryResult:
    yield from discover_query(section, "transactions")


def check(item: str, params: CheckParams, section: Section) -> CheckResult:
    trans = fields(section[item], "transactions")
    if trans is None:
        yield Result(state=State.UNKNOWN, summary="Transaction information unavailable")
        return
    start = trans.get("STARTDATE")
    if not start or start == "(null)":
        yield Result(state=State.UNKNOWN, summary="Transaction start timestamp unavailable")
        return
    try:
        started = datetime.strptime(start[:14], "%Y%m%d%H%M%S")
        age = max(0.0, (datetime.now() - started).total_seconds())
    except ValueError:
        yield Result(state=State.UNKNOWN, summary="Invalid transaction timestamp")
        return
    yield from check_levels(
        age,
        levels_upper=params["age"],
        metric_name="maxdb_transaction_age_seconds",
        label="Sample transaction age",
        render_func=render.timespan,
    )
    yield Result(state=State.OK, summary="Only first transaction sampled; not necessarily oldest")


agent_section_maxdb_transactions = AgentSection(
    name="maxdb_transactions", parse_function=parse_json
)
check_plugin_maxdb_transactions = CheckPlugin(
    name="maxdb_transactions",
    service_name="MaxDB %s Transactions",
    discovery_function=discover,
    check_function=check,
    check_ruleset_name="maxdb_transactions",
    check_default_parameters={"age": ("fixed", (900.0, 3600.0))},
)
