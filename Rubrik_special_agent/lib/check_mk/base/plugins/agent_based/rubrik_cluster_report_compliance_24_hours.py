
#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# 2023, marcus.klein@iteratio.com

from .agent_based_api.v1 import (
    register,
    Result,
    Service,
    State,
)

import ast

def parse_rubrik_cluster_compliance_24_hours(string_table):
    try:
        out = ast.literal_eval(string_table[0][0])
    except:
        out = {}
    return out


register.agent_section(
    name="rubrik_cluster_compliance_24_hours",
    parse_function=parse_rubrik_cluster_compliance_24_hours,
)


def discover_rubrik_cluster_compliance_24_hours(section):
    if section:
        yield Service()

def check_rubrik_cluster_compliance_24_hours(section):
    if not section:
        yield Result(state=State.UNKNOWN, summary="No Data")
        return

    print(section)
    yield Result(
        state=State.WARN if section['numberOfInComplianceSnapshots'] < 0 else State.OK,
        summary=f"Snapshots in compliance: {section['numberOfInComplianceSnapshots']}, Snapshots out of compliance: {section['numberOfOutOfComplianceSnapshots']}",
        details=f"Total protcted objects: {section['totalProtected']}, Snapshots awaiting first full: {section['numberAwaitingFirstFull']}"
    )

    # yield Result(
    #     state=State.WARN if section['numberOfOutOfComplianceSnapshots'] > 0 else State.OK,
    #     summary=f"",
    # )

    # yield Result(
    #     state=State.WARN if section['percentOutOfCompliance'] > 0 else State.OK,
    #     summary=f"% out of compliance: {section['percentOutOfCompliance']}",
    # )

    # yield Result(
    #     state=State.WARN if section['percentInCompliance'] < 100 else State.OK,
    #     summary=f"% in compliance: {section['percentInCompliance']}",
    # )


register.check_plugin(
    name="rubrik_cluster_compliance_24_hours",
    service_name="Rubrik Compliance 24 Hours",
    discovery_function=discover_rubrik_cluster_compliance_24_hours,
    check_function=check_rubrik_cluster_compliance_24_hours,
)
