#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import NamedTuple
from .agent_based_api.v1 import (
    register,
    exists,
    SNMPTree,
    Service,
    Result,
    State,
)


class Tape_Drive_Info(NamedTuple):
    name: str
    ident_number: str
    vendor: str
    version: str
    element_name: str


def parse_dell_tape_drive_info(string_table):
    return Tape_Drive_Info(*string_table[0])


def check_dell_emc_ml3_info(section):
    yield Result(
        state=State.OK,
        summary=
        f"Name: {section.name[0]}, IdentifyingNumber: {section.ident_number[0]}, Version: {section.version[0]}",
        details=
        f"Name: {section.name[0]}, IdentifyingNumber: {section.ident_number[0]}, Vendor: {section.vendor[0]}, Version: {section.version[0]}, ElementName: {section.element_name[0]}",
    )


def discover_dell_tape_drive_info(section):
    if section:
        yield Service()


register.snmp_section(
    name='dell_emc_ml3_info',
    detect=exists(".1.3.6.1.4.1.14851.3.1.6.2.1.*"),
    parse_function=parse_dell_tape_drive_info,
    fetch=[
        SNMPTree(base='.1.3.6.1.4.1.14851.3.1', oids=[
            "3",
        ]),
    ],
)

register.check_plugin(
    name="dell_emc_ml3_info",
    service_name="Info",
    discovery_function=discover_dell_tape_drive_info,
    check_function=check_dell_emc_ml3_info,
)
