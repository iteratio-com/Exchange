#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .agent_based_api.v1 import (register, exists, SNMPTree, Service, Result,
                                 State as state, check_levels, render)


def discover_tape_drive(section):
    for tape_drive in section:
        yield Service(item=tape_drive)


def parse_dell_emc_ml3_drive(string_table):
    parsed = {}
    for index, name, ava, cleaning, power_on_hours, op_status in string_table[
            0]:
        parsed[index] = (name, ava, cleaning, power_on_hours, op_status)
    return parsed


def check_dell_emc_ml3_drive(item, params, section):
    name, ava, cleaning, power_on_hours, op_status = section.get(item)
    yield Result(state=state.OK, summary=name)
    ava_map = {
        '1': (state.WARN, 'other'),
        '2': (state.UNKNOWN, 'unknown'),
        '3': (state.OK, 'runningFullPower'),
        '4': (state.WARN, 'warning'),
        '5': (state.WARN, 'inTest'),
        '6': (state.WARN, 'notApplicable'),
        '7': (state.WARN, 'powerOff'),
        '8': (state.WARN, 'offLine'),
        '9': (state.WARN, 'offDuty'),
        '10': (state.CRIT, 'degraded'),
        '11': (state.WARN, 'notInstalled'),
        '12': (state.CRIT, 'installError'),
        '13': (state.WARN, 'powerSaveUnknown'),
        '14': (state.WARN, 'powerSaveLowPowerMode'),
        '15': (state.WARN, 'powerSaveStandby'),
        '16': (state.WARN, 'powerCycle'),
        '17': (state.WARN, 'powerSaveWarning'),
        '18': (state.WARN, 'paused'),
        '19': (state.WARN, 'notReady'),
        '20': (state.WARN, 'notConfigured'),
        '21': (state.WARN, 'quiesced'),
    }
    status, txt = ava_map.get(ava, (state.UNKNOWN, "unknown Status Code"))
    if params.get('ava_map'):
        status = params['ava_map'].get(ava)
        status = state(status)
    yield Result(state=status, summary=txt)

    cleaning_map = {
        '1': (params.get('cleaning_needed', state.WARN), 'cleaning needed'),
        '2': (state.OK, 'no cleaning needed')
    }
    status, txt = cleaning_map.get(cleaning, (state.UNKNOWN, 'unknown Status'))
    yield Result(state=status, summary="Cleaning Status: " + txt)

    if power_on_hours:
        yield from check_levels(
            int(power_on_hours) * 3600,
            metric_name="uptime",
            render_func=render.timespan,
            label="Uptime",
        )

    op_status_map = {
        '0': (state.UNKNOWN, 'unknown'),
        '1': (state.WARN, 'other'),
        '2': (state.OK, 'ok'),
        '3': (state.WARN, 'degraded'),
        '4': (state.WARN, 'stressed'),
        '5': (state.WARN, 'predictiveFailure'),
        '6': (state.CRIT, 'error'),
        '7': (state.CRIT, 'non-RecoverableError'),
        '8': (state.WARN, 'starting'),
        '9': (state.WARN, 'stopping'),
        '10': (state.WARN, 'stopped'),
        '11': (state.WARN, 'inService'),
        '12': (state.WARN, 'noContact'),
        '13': (state.CRIT, 'lostCommunication'),
        '14': (state.WARN, 'aborted'),
        '15': (state.WARN, 'dormant'),
        '16': (state.CRIT, 'supportingEntityInError'),
        '17': (state.OK, 'completed'),
        '18': (state.WARN, 'powerMode'),
        '19': (state.WARN, 'dMTFReserved'),
    }
    status, txt = op_status_map.get(op_status,
                                    (state.UNKNOWN, 'unknown status'))
    if params.get('opa_map'):
        status = params['opa_map'].get(ava, status)
        status = state(status)
    yield Result(state=status, summary="Operational Status: " + txt)


register.snmp_section(
    name='dell_emc_ml3_drive',
    detect=exists(".1.3.6.1.4.1.14851.3.1.6.2.1.*"),
    parse_function=parse_dell_emc_ml3_drive,
    fetch=[
        SNMPTree(base='.1.3.6.1.4.1.14851.3.1.6.2.1',
                 oids=[
                     "1",
                     "3",
                     "5",
                     "6",
                     "10",
                     "11",
                 ]),
    ],
)

register.check_plugin(
    name="dell_emc_ml3_drive",
    service_name="Tape Drive %s",
    discovery_function=discover_tape_drive,
    check_function=check_dell_emc_ml3_drive,
    check_ruleset_name='dell_emc_ml3_drive',
    check_default_parameters={},
)
