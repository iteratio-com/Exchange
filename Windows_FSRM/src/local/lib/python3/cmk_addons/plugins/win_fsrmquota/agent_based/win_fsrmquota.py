#!/usr/bin/env python3

from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    AgentSection,
    DiscoveryResult,
    Metric,
    Result,
    Service,
    State,
    StringTable,
    get_value_store,
)

from cmk.plugins.lib.df import (
    df_check_filesystem_single,
    INODES_DEFAULT_PARAMS,
    SHOW_LEVELS_DEFAULT,
    MAGIC_FACTOR_DEFAULT_PARAMS,
    TREND_DEFAULT_PARAMS,
)

from dataclasses import dataclass
from collections.abc import Mapping
from typing import Any


FILESYSTEM_DEFAULT_LEVELS: Mapping[str, Any] = {
    "levels": (95.0, 98.0),  # warn/crit in percent
}


FILESYSTEM_DEFAULT_PARAMS: Mapping[str, Any] = {
    **FILESYSTEM_DEFAULT_LEVELS,
    **MAGIC_FACTOR_DEFAULT_PARAMS,
    **SHOW_LEVELS_DEFAULT,
    **INODES_DEFAULT_PARAMS,
    "show_reserved": False,
    **TREND_DEFAULT_PARAMS,
}


@dataclass
class SingleQuota:
    size: float
    usage: float


WinFSRMQuotaSection = dict[str, SingleQuota]


def parse_win_fsrmquota(string_table: StringTable) -> WinFSRMQuotaSection:
    section = {}
    factor = 1000000
    for path, size, usage in string_table:
        section[path] = SingleQuota(size=float(size) / factor, usage=float(usage) / factor)
    return section


agent_section_win_fsrmquota = AgentSection(
    name="win_fsrmquota",
    parse_function=parse_win_fsrmquota,
)


def discovery_win_fsrmquota(section: WinFSRMQuotaSection) -> DiscoveryResult:
    for path in section:
        yield Service(item=path)


def check_win_fsrmquota(
    item: str, params: Mapping[str, Any], section: WinFSRMQuotaSection
) -> CheckResult:
    if not (quota := section.get(item)):
        return

    yield from df_check_filesystem_single(
        value_store=get_value_store(),
        mountpoint=item,
        filesystem_size=quota.size,
        free_space=quota.size - quota.usage,
        reserved_space=0,
        inodes_total=None,
        inodes_avail=None,
        params=params,
    )


check_plugin_win_fsrmquotas = CheckPlugin(
    name="win_fsrmquota",
    service_name="FSRM Quota %s",
    discovery_function=discovery_win_fsrmquota,
    check_function=check_win_fsrmquota,
    check_default_parameters=FILESYSTEM_DEFAULT_PARAMS,
    check_ruleset_name="filesystem",
)
