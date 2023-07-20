#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from typing import Mapping, Any
from .agent_based_api.v1 import register, Service, Result, State, render, check_levels
from .agent_based_api.v1.type_defs import CheckResult, DiscoveryResult, StringTable

MaxDBBackupSection = dict[str, Any]


def parse_maxdb_backup(string_table: StringTable) -> MaxDBBackupSection:
    current_time = int((datetime.now() - datetime(1970, 1, 1)).total_seconds())
    parsed, srv = {}, ""
    for line in string_table:
        if line[0] and line[0].strip() in ["OK", "END", "CONTINUE"]:
            continue
        if line[0].startswith("[["):
            srv = line[0].replace("[[", "").replace("]]", "")
            parsed.setdefault(srv, {})
        elif len(line) == 7:
            job, job_type, start, stop, result, error_msg, out = line
            if start == stop:
                duration = 0
                begin = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
            else:
                begin = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
                end = datetime.strptime(stop, "%Y-%m-%d %H:%M:%S")
                duration = (end - begin).total_seconds()
            age = current_time - int((begin - datetime(1970, 1, 1)).total_seconds())
            parsed[srv].setdefault(job, {})
            parsed[srv][job] = {
                "start": start,
                "stop": stop,
                "duration": duration,
                "error_msg": error_msg.strip(),
                "type": job_type.strip(),
                "result_code": result.strip(),
                "age": age,
            }
            if result.strip() != "0" or error_msg.strip():
                parsed[srv].setdefault("error_jobs", []).append(job)
            if job.startswith("DAT"):
                if parsed[srv].get("last_data") and parsed[srv]["last_data"][0] > age:
                    parsed[srv]["last_data"] = [age, job]
                elif not parsed[srv].get("last_data"):
                    parsed[srv]["last_data"] = [age, job]
            elif job.startswith("LOG"):
                if parsed[srv].get("last_log") and parsed[srv]["last_log"][0] > age:
                    parsed[srv]["last_log"] = [age, job]
                elif not parsed[srv].get("last_log"):
                    parsed[srv]["last_log"] = [age, job]
    return parsed


register.agent_section(
    name="maxdb_backup",
    parse_function=parse_maxdb_backup,
)


def discover_maxdb_backup(section: MaxDBBackupSection) -> DiscoveryResult:
    for item in section:
        if item:
            yield Service(item=item)


def check_maxdb_backup(
    item: str, params: Mapping[str, Any], section: MaxDBBackupSection
) -> CheckResult:
    if item not in section:
        yield Result(state=State.UNKNOWN, summary=f"No Data for {item} found")
        return
    data = section.get(item)

    if not data.get("error_jobs"):
        yield Result(state=State.OK, summary="No Backup job errors")
    else:
        txt = []
        for job in data["error_jobs"]:
            job_infos = data.get(job)
            txt += [
                f"{job} - started: {job_infos.get('start')} - duration: {render.timespan(job_infos.get('duration'))}"
                f" - Type: {job_infos.get('type')} - Age: {render.timespan(job_infos.get('age'))}"
                f" - MSG: {job_infos.get('error_msg')}"
            ]
        yield Result(
            state=State.WARN,
            summary=f"There are {len(data.get('error_jobs'))} Jobs with Error (see long output)",
            details="\n".join(txt),
        )

    last_data, last_data_name = data.get("last_data", (None, None))
    last_log, last_log_name = data.get("last_log", (None, None))
    if last_data:
        yield from check_levels(
            last_data,
            levels_upper=params.get("age_data"),
            metric_name="last_data_job",
            label=f"Last Data Backup Job ({last_data_name})",
            render_func=render.timespan,
        )
    else:
        yield Result(state=State.OK, summary="No data jobs found")

    if last_log:
        yield from check_levels(
            last_log,
            levels_upper=params.get("age_log"),
            metric_name="last_log_job",
            label=f"Last Log Backup Job ({last_log_name})",
            render_func=render.timespan,
        )
    else:
        yield Result(state=State.OK, summary="No log jobs found")


register.check_plugin(
    name="maxdb_backup",
    service_name="MaxDB %s Backup",
    discovery_function=discover_maxdb_backup,
    check_ruleset_name="maxdb_backups",
    check_default_parameters={},
    check_function=check_maxdb_backup,
)
