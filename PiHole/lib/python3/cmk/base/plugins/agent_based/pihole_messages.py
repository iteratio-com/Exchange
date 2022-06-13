#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

from .agent_based_api.v1 import (register, Service, Result, State, render,
                                 check_levels)


def parse_pihole_messages(string_table):
    try:
        data = eval(string_table[0][0])
    except:
        data = ''.join(string_table)
    return data


register.agent_section(name="pihole_messages",
                       parse_function=parse_pihole_messages)


def discover_pihole_messages(section):
    if section:
        yield Service()


def check_pihole_messages(params, section):
    if not section:
        yield Result(state=State.UNKNOWN, summary="No Output found")
        return

    if isinstance(section, str):
        yield Result(state=State.UNKNOWN, summary=section)
        return

    yield from check_levels(
        label="Total Messages",
        value=len(section.get("messages", [])),
        levels_upper=params.get('levels_upper', (None, None)),
        metric_name="total_messages",
        render_func=int,
    )

    out = {}
    for msg in section.get("messages", []):
        if msg.get('type') in out:
            out[msg.get('type')] += 1
        else:
            out[msg.get('type')] = 1

    for i in out:
        result, _metric = check_levels(
            label=f"{i} Messages",
            value=out[i],
            levels_upper=params.get(f'levels_{i}', (None, None)),
            metric_name=f"{i}_messages",
            render_func=int,
        )
        yield result

    for i, msg in enumerate(section.get("messages", [])):
        yield Result(
            state=State.OK,
            notice=
            f"{render.datetime(msg.get('timestamp'))} - Type: {msg.get('type')} - Message: {msg.get('message')}",
            details=
            f"{render.datetime(msg.get('timestamp'))} - Type: {msg.get('type')} - Message: {msg.get('message')}"
        )


register.check_plugin(
    name="pihole_messages",
    service_name="Pi-hole Messages",
    discovery_function=discover_pihole_messages,
    check_default_parameters={},
    check_function=check_pihole_messages,
    check_ruleset_name="pihole_messages",
)