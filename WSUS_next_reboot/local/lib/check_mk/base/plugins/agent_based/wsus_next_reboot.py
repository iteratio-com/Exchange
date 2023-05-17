#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# 2023, marcus.klein@iteratio.com

# <<<wsus_next_reboot:sep(59)>>>
# NoAutoUpdate;0
# AUOptions;4
# ScheduledInstallDay;4
# ScheduledInstallTime;10
# ScheduledInstallEveryWeek;1
# UseWUServer;1
# DetectionFrequencyEnabled;1
# DetectionFrequency;6
# AutoInstallMinorUpdates;1
# IncludeRecommendedUpdates;1
# RescheduleWaitTimeEnabled;1
# RescheduleWaitTime;60
# AlwaysAutoRebootAtScheduledTime;1
# AlwaysAutoRebootAtScheduledTimeMinutes;15
# AllowMUUpdateService;1
# BaseUtcOffsetSeconds;7200

import livestatus, os, datetime, time, pytz
from cmk.base.check_api import host_name as heimwerker

from .agent_based_api.v1 import (
    register,
    Result,
    Service,
    State,
)

def parse_wsus_next_reboot(string_table):
    section = {}
    for name, value in string_table:
        section[name] = value
    return section


register.agent_section(
    name="wsus_next_reboot",
    parse_function=parse_wsus_next_reboot,
)


def discover_wsus_next_reboot(section):
    if section:
        yield Service()


def get_and_set_dawntime(DowntimeStart, DowntimeDuration, DowntimeUser, DowntimeComment):
    omd_root = os.environ["OMD_ROOT"]
    socket_path = "unix:" + omd_root + "/tmp/run/live"
    res = livestatus.SingleSiteConnection(socket_path).query_table(
        f"GET downtimes\nColumns: host_downtimes_with_extra_info\nFilter: host_name = {heimwerker()}\nFilter: comment = {DowntimeComment}"
    )

    # id, author, comment, origin, entry_time, start_time, end_time, fixed, duration, recurring and is_pending
    if not res:
        livestatus.SingleSiteConnection(socket_path).send_command(
            f"COMMAND [{int(time.time())}] SCHEDULE_HOST_DOWNTIME;{heimwerker()};{DowntimeStart};{int(DowntimeStart) + DowntimeDuration};1;0;0;{DowntimeUser};{DowntimeComment}"
        )

def next_weekday(now, weekday):
    days_ahead = weekday - now.weekday()
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7
    return now.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days_ahead)


def check_wsus_next_reboot(params, section):
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data from host")
        return

    InstallDay = {
        '0': ('Daily', 7),
        '1': ('Sunday', 6),
        '2': ('Monday', 0),
        '3': ('Tuesday', 1),
        '4': ('Wednesday', 2),
        '5': ('Thursday', 4),
        '6': ('Friday', 3),
        '7': ('Saturday', 5),
    }.get(section.get('ScheduledInstallDay'), 'Unknown')

    if InstallDay == 'Unknown':
        yield Result(state=State(params.get("default_state",1)), summary="No update day information in registry found.")
        return

    AUOptions = {
        '2': ('Notify before download', 'NoDowntime'),
        '3': ('Automatically download and notify of installation', 'NoDowntime'),
        '4': ('Automatic download and scheduled installation', 'SetDowntime'),
        '5': ('Automatic Updates is required, but end users can configure it', 'NoDowntime'),
        '7': ('Auto Download, Notify to install, Notify to Restart', 'NoDowntime'),
    }.get(section.get('AUOptions'), 'Unknown')
    
    InstallTimeHour = int(section.get('ScheduledInstallTime', 0))
    InstallTimeSeconds = InstallTimeHour * 3600
    InstallTimeText = f"{str(InstallTimeHour)}:00:00"
    HostBaseUTCOffsetSeconds = int(section.get('BaseUtcOffsetSeconds'))
    CMKServerUtcOffsetSeconds = round((datetime.datetime.fromtimestamp(time.time()) - datetime.datetime.utcfromtimestamp(time.time())).total_seconds())
    SecondsToAdd = CMKServerUtcOffsetSeconds - HostBaseUTCOffsetSeconds + InstallTimeSeconds
    CurrentHour = datetime.datetime.now().hour

    if InstallDay[0] == 'Daily' and CurrentHour < InstallTimeHour:
        SchedDay = int(datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).strftime('%s'))
    elif InstallDay[0] == 'Daily' and CurrentHour >= InstallTimeHour:
        tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
        SchedDay = int(tomorrow.replace(hour=0,minute=0,second=0,microsecond=0).strftime('%s'))
    else:
        SchedDay = int(next_weekday(datetime.datetime.now(), InstallDay[1]).strftime('%s'))

    DowntimeStart = SchedDay + SecondsToAdd

    yield Result(state=State.OK,
                 summary=f"Next scheduled installation: {InstallDay[0]}, {InstallTimeText}")
    yield Result(state=State.OK, notice=f"Base UTC offset in seconds: {HostBaseUTCOffsetSeconds}")
    yield Result(state=State.OK, notice=f"Next downtime in unix epoch: {DowntimeStart}")
    yield Result(state=State.OK, summary=f"Mode: {AUOptions[0]}")

    if AUOptions[1] == 'SetDowntime':
        get_and_set_dawntime(DowntimeStart, DowntimeDuration=params.get('downtime_duration', 7200), DowntimeUser=params.get("downtime_author", "automation"), DowntimeComment=params.get("downtime_comment", "WSUS set downtime"))

register.check_plugin(
    name="wsus_next_reboot",
    sections=["wsus_next_reboot"],
    service_name="WSUS next reboot",
    discovery_function=discover_wsus_next_reboot,
    check_function=check_wsus_next_reboot,
    check_default_parameters={"downtime_comment":"WSUS set downtime", "downtime_author":"autonation","downtime_duration":7200,"default_state":1},
    check_ruleset_name="wsus_next_reboot",
)
