#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import datetime
import dateutil.parser

from .agent_based_api.v1 import (
    exists,
    check_levels,
    render,
    register,
    SNMPTree,
    Service,
    Result,
    State,
)


def parse_snmp_systemtime(string_table):
    """This is the number decoder for this
    A date-time specification.
            field  octets  contents                  range
            -----  ------  --------                  -----
              1      1-2   year*                     0..65536
              2       3    month                     1..12
              3       4    day                       1..31
              4       5    hour                      0..23
              5       6    minutes                   0..59
              6       7    seconds                   0..60
                           (use 60 for leap-second)
              7       8    deci-seconds              0..9
              8       9    direction from UTC        '+' / '-'
              9      10    hours from UTC*           0..13
             10      11    minutes from UTC          0..59
    * Notes:
            - the value of year is in network-byte order
            - daylight saving time in New Zealand is +13
    For example, Tuesday May 26, 1992 at 1:30:15 PM EDT would be
            displayed as:
                 1992-5-26,13:30:15.0,-4:0
    Note that if only local time is known, then timezone
            information (fields 8-10) is not present.

    :param octet_string: string of octal values, like "07 E2 02 0E 0C 0A 38 00 2B 01 00"
    :return: 2018-02-11 23:06:43
    """
    parsed = {}
    octet_string = string_table[0][0]
    real_utc = False
    if len(octet_string) == 11:
        output_string = "%04d-%02d-%02d %02d:%02d:%02d, %s%02d:%02d" % (
            ((ord(octet_string[0]) * 16**2) + ord(octet_string[1])), ord(octet_string[2]),
            ord(octet_string[3]), ord(octet_string[4]), ord(octet_string[5]), ord(
                octet_string[6]), octet_string[8], ord(octet_string[9]), ord(octet_string[10]))
        real_utc = True
    elif len(octet_string) < 11:
        output_string = "%04d-%02d-%02d %02d:%02d:%02d.%02d, +00:00" % ((
            (ord(octet_string[0]) * 16**2) + ord(octet_string[1])), ord(
                octet_string[2]), ord(octet_string[3]), ord(octet_string[4]), ord(
                    octet_string[5]), ord(octet_string[6]), ord(octet_string[7]))
    else:
        return
    diff = 0
    if "00:00" in output_string[-5:] and not real_utc:
        utctime = time.mktime(time.gmtime())
        localtime = time.mktime(time.localtime())
        diff = localtime - utctime
    snmp_time = dateutil.parser.parse(output_string)
    snmp_time = time.mktime(datetime.datetime.utctimetuple(snmp_time)) - diff
    now = datetime.datetime.utcnow()
    now = int(time.mktime(datetime.datetime.utctimetuple(now)))
    delta_time = now - snmp_time
    parsed = {'delta': delta_time, 'snmp_time': snmp_time, 'out_string': output_string}
    return parsed


register.snmp_section(
    name="snmp_systemtime",
    detect=exists(".1.3.6.1.2.1.25.1.2.0"),
    parse_function=parse_snmp_systemtime,
    fetch=SNMPTree(
        base='.1.3.6.1.2.1.25.1',
        oids=['2'],
    ),
)


def discover_snmp_system_time_offset(section):
    if section:
        yield Service()


def check_snmp_system_time_offset(params, section):
    if not section:
        yield Result(state=State.UNKNOWN, summary="No Data from SNMP")
        return

    yield Result(state=State.OK,
                 summary=f"Time from Device: {section.get('out_string').replace(',','')}")

    yield from check_levels(
        section.get('delta'),
        metric_name="time_offset",
        label="Time difference",
        render_func=render.timespan,
        levels_upper=params.get('levels'),
    )


register.check_plugin(
    name="snmp_systemtime",
    service_name="System Time Offset",
    discovery_function=discover_snmp_system_time_offset,
    check_function=check_snmp_system_time_offset,
    check_default_parameters={'levels': (100, 180)},
    check_ruleset_name="snmp_systemtime_group",
)
