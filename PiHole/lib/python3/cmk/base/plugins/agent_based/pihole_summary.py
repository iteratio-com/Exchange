#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

from .agent_based_api.v1 import register, Service, Result, State, render, check_levels
import time


def parse_pihole_summary(string_table):
    try:
        data = eval(string_table[0][0])
    except:
        data = ''.join(string_table)

    parsed = {
        'state': data.get('status', 'No output'),
        'gravity': data.get('gravity_last_updated'),
        'summary': data
    }
    return parsed


register.agent_section(name="pihole_summary",
                       parse_function=parse_pihole_summary)


def discover_pihole_state(section):
    if section.get('state'):
        yield Service()


def check_pihole_state(params, section):
    if not section.get('state'):
        yield Result(state=State.UNKNOWN, summary="No Output found")
        return

    status = section.get('state')
    state = State.OK if status.lower() == 'enabled' else State(
        params.get('state', 3))
    yield Result(state=state, summary=f"Status: {status.title()}")


register.check_plugin(
    name="pihole_state",
    sections=['pihole_summary'],
    service_name="Pi-hole State",
    discovery_function=discover_pihole_state,
    check_default_parameters={'state': 1},
    check_function=check_pihole_state,
    check_ruleset_name="pihole_state",
)


def discover_pihole_summary(section):
    if section.get('summary', {}):
        yield Service()


def check_pihole_summary(params, section):
    if not section.get('summary', {}):
        yield Result(state=State.UNKNOWN, summary="No Output found")
        return

    data = section['summary']
    values = [
        ('Blocked Domains', 'domains_being_blocked', int, None, False),
        ('DNS Queries Today', 'dns_queries_today', int, None, False),
        ('Ads Blocked Today', 'ads_blocked_today', int, None, False),
        ('Ads Percentage Today', 'ads_percentage_today', render.percent,
         (0, 100), True),
        ('Unique Domains', 'unique_domains', int, None, True),
        ('Queries Forwarded', 'queries_forwarded', int, None, True),
        ('Queries Cached', 'queries_cached', int, None, True),
        ('Clients Ever Seen', 'clients_ever_seen', int, None, True),
        ('Unique Clients', 'unique_clients', int, None, True),
        ('reply NODATA', 'reply_NODATA', int, None, True),
        ('reply NXDOMAIN', 'reply_NXDOMAIN', int, None, True),
        ('reply CNAME', 'reply_CNAME', int, None, True),
        ('reply IP', 'reply_IP', int, None, True),
    ]
    for label, metric, render_func, bound, notice in values:
        yield from check_levels(
            label=label,
            value=data.get(metric),
            metric_name=metric,
            boundaries=bound,
            render_func=render_func,
            notice_only=notice,
        )


register.check_plugin(
    name="pihole_summary",
    sections=['pihole_summary'],
    service_name="Pi-hole Summary",
    discovery_function=discover_pihole_summary,
    check_default_parameters={'state': 1},
    check_function=check_pihole_summary,
    check_ruleset_name="pihole_summary",
)


def discover_pihole_gravity(section):
    if section.get('gravity'):
        yield Service()


def check_pihole_gravity(params, section):
    if not section.get('gravity', {}):
        yield Result(state=State.UNKNOWN, summary="No Output found")
        return

    data = section.get('gravity', {})  #
    if data.get('file_exists'):
        yield Result(state=State.OK, summary="Gravity File Exists")
    else:
        yield Result(State=State.CRIT, summary="No Gravity File!")

    if data.get('absolute'):
        current_time = time.time()
        device_time = data.get('absolute')

        yield from check_levels(label="Age",
                                value=current_time - device_time,
                                metric_name="gravity_last_updated",
                                levels_upper=params.get(
                                    'levels', (None, None)),
                                render_func=render.timespan)
        yield Result(
            state=State.OK,
            summary=f"Last updated: {render.datetime(data.get('absolute'))}")


register.check_plugin(
    name="pihole_gravity",
    sections=['pihole_summary'],
    service_name="Pi-hole Gravity",
    discovery_function=discover_pihole_gravity,
    check_default_parameters={},
    check_function=check_pihole_gravity,
    check_ruleset_name="pihole_gravity",
)