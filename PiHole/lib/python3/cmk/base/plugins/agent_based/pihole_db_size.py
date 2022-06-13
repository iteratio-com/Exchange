#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

from .agent_based_api.v1 import register, Service, Result, State, render, check_levels


def parse_pihole_db_size(string_table):
    try:
        data = eval(string_table[0][0])
    except:
        data = ''.join(string_table)
    return data


register.agent_section(name="pihole_db_size",
                       parse_function=parse_pihole_db_size)


def discover_pihole_db_size(section):
    if section:
        yield Service()


def check_pihole_db_size(params, section):
    if not section:
        yield Result(state=State.UNKNOWN, summary="No Output found")
        return

    if isinstance(section, str):
        yield Result(state=State.UNKNOWN, summary=section)
        return

    yield from check_levels(
        label="/etc/pihole/pihole-FTL.db",
        value=section.get("filesize"),
        levels_upper=params.get('levels_upper', (None, None)),
        levels_lower=params.get('levels_lower', (None, None)),
        metric_name="db_file_size",
        render_func=render.bytes,
    )


register.check_plugin(
    name="pihole_db_size",
    service_name="Pi-hole DB File Size",
    discovery_function=discover_pihole_db_size,
    check_default_parameters={},
    check_function=check_pihole_db_size,
    check_ruleset_name="pihole_db_size",
)