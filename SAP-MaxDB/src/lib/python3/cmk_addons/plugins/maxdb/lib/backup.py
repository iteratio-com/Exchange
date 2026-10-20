"""Shared MaxDB backup history evaluation."""

from datetime import datetime
from typing import TypeAlias

from cmk.agent_based.v2 import CheckResult, Metric, Result, State, check_levels, render
from cmk_addons.plugins.maxdb.lib.common import CheckParams, DatabaseData, Section

BackupRecord: TypeAlias = tuple[datetime, int, float]


def backup_records(obj: DatabaseData, kind: str) -> list[BackupRecord] | None:
    query = next((q for q in obj.get("queries", []) if q.get("query") == "backup_history"), None)
    if not query or query.get("status") != "ok":
        return None
    records: list[BackupRecord] = []
    for line in query.get("output", "").splitlines():
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 5 or parts[0].split("_", 1)[0] != kind:
            continue
        try:
            finished = datetime.strptime(parts[3], "%Y-%m-%d %H:%M:%S")
            started = datetime.strptime(parts[2], "%Y-%m-%d %H:%M:%S")
            records.append((finished, int(parts[4]), (finished - started).total_seconds()))
        except ValueError:
            continue
    return records


def check_backup(
    item: str, params: CheckParams, section: Section, kind: str, label: str
) -> CheckResult:
    records = backup_records(section[item], kind)
    if records is None:
        yield Result(state=State.UNKNOWN, summary="Backup history unavailable")
        return
    successes = [r for r in records if r[1] == 0]
    if not successes:
        yield Result(
            state=State.CRIT if records else State.UNKNOWN,
            summary=f"{label}: no successful backup in history",
        )
    else:
        latest = max(successes, key=lambda r: r[0])
        age = max(0.0, (datetime.now() - latest[0]).total_seconds())
        yield from check_levels(
            age,
            levels_upper=params["age"],
            metric_name=f"maxdb_backup_{kind.lower()}_age",
            label=f"{label} age",
            render_func=render.timespan,
        )
        yield Metric(f"maxdb_backup_{kind.lower()}_duration", latest[2])
    if records:
        latest_attempt = max(records, key=lambda r: r[0])
        if latest_attempt[1] != 0:
            yield Result(
                state=State(params["failed_state"]),
                summary=f"{label}: latest attempt failed (RC {latest_attempt[1]})",
            )
