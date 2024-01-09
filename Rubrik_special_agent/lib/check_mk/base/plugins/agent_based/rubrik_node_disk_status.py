#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# 2023, marcus.klein@iteratio.com

from typing import Any, Mapping

from .agent_based_api.v1 import Result, Service, State, get_value_store, register
from .agent_based_api.v1.type_defs import CheckResult, DiscoveryResult, StringTable
from .utils.df import FILESYSTEM_DEFAULT_PARAMS, df_check_filesystem_single
from .utils.rubrik_api import RubrikSection

from ast import literal_eval


def parse_rubrik_node_disk(string_table: StringTable) -> RubrikSection:
    out = []
    for elem in string_table:
        out += [literal_eval(elem[0])]

    if not out:
        return
    return {disk["id"]: disk for disk in out}


register.agent_section(
    name="rubrik_node_disk",
    parse_function=parse_rubrik_node_disk,
)


def discover_rubrik_node_disk(section: RubrikSection) -> DiscoveryResult:
    for disk in section:
        yield Service(item=disk)


def check_rubrik_node_disk(
    item: str, params: Mapping[str, Any], section: RubrikSection
) -> CheckResult:
    if not (disk := section.get(item)):
        return

    yield from df_check_filesystem_single(
        value_store=get_value_store(),
        mountpoint=disk["path"],
        filesystem_size=disk["capacityBytes"] / 1024**2,
        free_space=disk["unallocatedBytes"] / 1024**2,
        reserved_space=0,
        inodes_total=None,
        inodes_avail=None,
        params=params,
    )

    yield Result(
        state=State.OK if disk["status"] == "ACTIVE" else State.CRIT,
        summary=f"State: {disk['status']}",
        details=f"Mountpoint: {disk['path']}",
    )
    yield Result(
        state=State.OK if disk["isDegraded"] == False else State.CRIT,
        summary=f"Degraded: {disk['isDegraded']}",
    )
    yield Result(
        state=State.OK if disk["isEncrypted"] == True else State.WARN,
        summary=f"Encrypted: {disk['isEncrypted']}",
    )


register.check_plugin(
    name="rubrik_node_disk",
    service_name="Rubrik Disk %s",
    discovery_function=discover_rubrik_node_disk,
    check_function=check_rubrik_node_disk,
    check_ruleset_name="filesystem",
    check_default_parameters=FILESYSTEM_DEFAULT_PARAMS,
)
