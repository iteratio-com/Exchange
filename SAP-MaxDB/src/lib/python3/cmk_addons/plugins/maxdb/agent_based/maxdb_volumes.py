from time import time

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    State,
    get_value_store,
)
from cmk.plugins.lib.df import FILESYSTEM_DEFAULT_PARAMS, df_check_filesystem_single
from cmk_addons.plugins.maxdb.lib.common import (
    CheckParams,
    Section,
    discover_query,
    fields,
    number,
    parse_json,
)


def discover(section: Section) -> DiscoveryResult:
    yield from discover_query(section, "data_statistics")


def check(item: str, params: CheckParams, section: Section) -> CheckResult:
    data = fields(section[item], "data_statistics")
    state = fields(section[item], "dbm_state") or {}
    if data is None:
        yield Result(state=State.UNKNOWN, summary="Data statistics unavailable")
        return
    used = number(data, "USEDSIZE")
    total = number(data, "USABLESIZE")
    page_kb = number(state, "PAGESIZE_IN_KB")
    if used is None or total is None or page_kb is None or total <= 0 or page_kb <= 0:
        yield Result(state=State.UNKNOWN, summary="Data page size or capacity missing")
    else:
        total_bytes = total * page_kb * 1024
        used_bytes = used * page_kb * 1024
        yield from df_check_filesystem_single(
            value_store=get_value_store(),
            mountpoint="Data",
            filesystem_size=total_bytes,
            free_space=max(0, total_bytes - used_bytes),
            reserved_space=None,
            inodes_avail=None,
            inodes_total=None,
            params=params,
            this_time=time(),
        )
    for key in ("DATAFULL", "LOGFULL"):
        value = str(data.get(key) or state.get(key) or "").upper()
        if value in ("YES", "TRUE"):
            yield Result(state=State.CRIT, summary=f"{key}: {value}")


agent_section_maxdb_volumes = AgentSection(name="maxdb_volumes", parse_function=parse_json)
check_plugin_maxdb_volumes = CheckPlugin(
    name="maxdb_volumes",
    service_name="MaxDB %s Volumes",
    discovery_function=discover,
    check_function=check,
    check_ruleset_name="filesystem",
    check_default_parameters=FILESYSTEM_DEFAULT_PARAMS,
)
