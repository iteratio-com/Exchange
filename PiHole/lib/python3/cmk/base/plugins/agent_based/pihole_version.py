#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

from .agent_based_api.v1 import register, Service, Result, State, TableRow


def parse_pihole_version(string_table):
    try:
        data = eval(string_table[0][0])
    except:
        data = ''.join(string_table)
    return data


register.agent_section(name="pihole_version",
                       parse_function=parse_pihole_version)


def discover_pihole_version(section):
    if section:
        yield Service()


def check_pihole_version(params, section):
    if not section:
        yield Result(state=State.UNKNOWN, summary="No Output found")
        return

    if isinstance(section, str):
        yield Result(state=State.UNKNOWN, summary=section)
        return

    for i in ('core', 'web', 'FTL'):
        if section.get(f"{i}_update") != None and section.get(
                f"{i}_update") == True:
            yield Result(
                state=State(params.get(i, 0)),
                summary=
                f'Component {i.title() if i != "FTL" else i}: {section.get(f"{i}_current")}, new avaiable Version {section.get(f"{i}_latest")}'
            )
        else:
            yield Result(
                state=State.OK,
                summary=
                f'Component {i.title() if i != "FTL" else i}: {section.get(f"{i}_current")}'
            )


register.check_plugin(
    name="pihole_version",
    service_name="Pi-hole Update",
    discovery_function=discover_pihole_version,
    check_default_parameters={
        'core': 0,
        'web': 0,
        'FTL': 0
    },
    check_function=check_pihole_version,
    check_ruleset_name="pihole_version",
)


def inv_pihole_version(section):
    path = ["software", "applications", 'pi-hole']
    for i in ('core', 'web', 'FTL'):
        yield TableRow(
            path=path,
            key_columns={"component": i.title() if i != 'FTL' else 'FTL'},
            inventory_columns={
                "version": section.get(f'{i}_current'),
            },
        )


register.inventory_plugin(
    name="inv_pihole_version",
    sections=['pihole_version'],
    inventory_function=inv_pihole_version,
)