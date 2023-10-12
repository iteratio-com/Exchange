#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# 2023, marcus.klein@iteratio.com

from .agent_based_api.v1 import (
    register,
    Result,
    Service,
    State,
    get_value_store,
)

from .utils.df import df_check_filesystem_single, FILESYSTEM_DEFAULT_LEVELS

import ast


def parse_rubrik_node_disk(string_table):
    out = {}
    if not string_table:
        return {}
    string_table = ast.literal_eval(string_table[0][0])
    for disk in string_table:
        name = disk["id"]
        out[name] = disk
    return out


register.agent_section(
    name="rubrik_node_disk",
    parse_function=parse_rubrik_node_disk,
)


def discover_rubrik_node_disk(section):
    for item in section:
        yield Service(item=item)


def check_rubrik_node_disk(item, params, section):
    if not section or item not in section:
        yield Result(state=State.UNKNOWN, summary="No data from host")
        return

    disk = section[item]

    yield from df_check_filesystem_single(
        value_store=get_value_store(),
        mountpoint=disk["path"],
        size_mb=disk["capacityBytes"] / 1024**2,
        avail_mb=disk["unallocatedBytes"] / 1024**2,
        reserved_mb=0,
        inodes_total=None,
        inodes_avail=None,
        params=params,
    )

    yield Result(
        state=State.CRIT if disk["status"] != "ACTIVE" else State.OK,
        summary=f"State: {disk['status']}",
        details=f"Mountpoint: {disk['path']}",
    )
    yield Result(
        state=State.CRIT if disk["isDegraded"] != False else State.OK,
        summary=f"Degraded: {disk['isDegraded']}",
    )
    yield Result(
        state=State.WARN if disk["isEncrypted"] != True else State.OK,
        summary=f"Encrypted: {disk['isEncrypted']}",
    )


register.check_plugin(
    name="rubrik_node_disk",
    service_name="Rubrik Disk %s",
    discovery_function=discover_rubrik_node_disk,
    check_function=check_rubrik_node_disk,
    check_ruleset_name="filesystem",
    check_default_parameters=FILESYSTEM_DEFAULT_LEVELS,
)
