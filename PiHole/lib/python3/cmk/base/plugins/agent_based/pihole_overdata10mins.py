#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

from .agent_based_api.v1 import register, Service, Result, State, check_levels, render


def parse_pihole_overdata10mins(string_table):
    try:
        data = eval(string_table[0][0])
    except:
        data = ''.join(string_table)
        return data

    return {
        'domains_over_time':
        max([(value, int(key))
             for key, value in data.get('domains_over_time', {}).items()]),
        'ads_over_time':
        max([(value, int(key))
             for key, value in data.get('ads_over_time', {}).items()])
    }


register.agent_section(name="pihole_overdata10mins",
                       parse_function=parse_pihole_overdata10mins)


def discover_pihole_overdata10mins(section):
    if section:
        yield Service()


def check_pihole_overdata10mins(params, section):
    if not section:
        yield Result(state=State.UNKNOWN, summary="No Output found")
        return

    if isinstance(section, str):
        yield Result(state=State.UNKNOWN, summary=section)
        return

    domains_over_time, domains_time = section.get('domains_over_time',
                                                  (None, None))

    ads_over_time, ads_time = section.get('ads_over_time', (None, None))
    yield from check_levels(
        value=domains_over_time,
        label=f"Domains over the last 10mins ({render.datetime(domains_time)})",
        render_func=int,
        levels_upper=params.get('levels_domains_over_time_10min',
                                (None, None)),
        metric_name="domains_over_time_10min",
    )
    yield from check_levels(
        value=ads_over_time,
        label=f"Ads blocked over the last 10mins ({render.datetime(ads_time)})",
        render_func=int,
        levels_upper=params.get('levels_ads_over_time', (None, None)),
        metric_name="ads_over_time_10min",
    )


register.check_plugin(
    name="pihole_overdata10mins",
    service_name="Pi-hole over Time Data 10mins",
    discovery_function=discover_pihole_overdata10mins,
    check_default_parameters={},
    check_function=check_pihole_overdata10mins,
    check_ruleset_name="pihole_overdata10mins",
)
