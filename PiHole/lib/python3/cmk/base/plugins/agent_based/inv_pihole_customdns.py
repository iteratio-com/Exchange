#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

from .agent_based_api.v1 import register, TableRow


def parse_pihole_customdns(string_table):
    try:
        data = eval(string_table[0][0])
    except:
        data = ''.join(string_table)

    return {'data': sorted(data.get('data', []), key=lambda entry: entry[0])}


register.agent_section(name="pihole_customdns",
                       parse_function=parse_pihole_customdns)


def inv_pihole_customdns(section):
    path = ["networking", "Custom_DNS_records"]
    if section.get('data', []):
        for host, ip_address in section.get('data', []):
            yield TableRow(
                path=path,
                key_columns={"host": host},
                inventory_columns={
                    "ip_address": ip_address,
                },
            )


register.inventory_plugin(
    name="inv_pihole_customdns",
    sections=['pihole_customdns'],
    inventory_function=inv_pihole_customdns,
)