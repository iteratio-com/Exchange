#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .agent_based_api.v1 import (register, exists, SNMPTree, Service, Result,
                                 State as state)


def discover_tape_drive_power_supply(section):
    for tape_drive in section:
        yield Service(item=tape_drive)


def parse_dell_emc_ml3_drive_power_supply(string_table):
    parsed = {}
    for index, ps1, ps2, serialno in string_table[0]:
        if ps1 != "":
            parsed[index + ".1"] = (ps1, serialno)
        if ps2 != "":
            parsed[index + ".2"] = (ps2, serialno)
    return parsed


def check_dell_emc_ml3_drive_power_supply(item, section):
    ps, serialno = section.get(item)

    ps_map = {
        '1': (state.OK, 'not installed'),
        '2': (state.OK, 'ok'),
        '3': (state.WARN, 'not ok'),
    }
    status, txt = ps_map.get(ps, (state.WARN, "unknown Status Code"))

    yield Result(state=status, summary=f"PowerSupply Status: {txt}")
    if serialno:
        yield Result(state=state.OK, summary=f"Chassis SerialNo: {serialno}")


register.snmp_section(
    name='dell_emc_ml3_drive_supply',
    detect=exists(".1.3.6.1.4.1.14851.3.1.6.2.1.*"),
    parse_function=parse_dell_emc_ml3_drive_power_supply,
    fetch=[
        SNMPTree(
            base='.1.3.6.1.4.1.2.6.257.1.3.2.1',
            oids=[
                "1",  # index
                "3",  # frame power supply 1 status
                "4",  # frame power supply 2 status
                "9",  # serial number
            ]),
    ],
)

register.check_plugin(
    name="dell_emc_ml3_drive_supply",
    service_name="Drive power supply %s",
    discovery_function=discover_tape_drive_power_supply,
    check_function=check_dell_emc_ml3_drive_power_supply,
)
