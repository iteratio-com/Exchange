"""Shared parsing and discovery helpers for MaxDB agent sections."""

import json
import re
from collections.abc import Iterator, Mapping
from typing import Any, TypeAlias

from cmk.agent_based.v2 import DiscoveryResult, Service, StringTable

Query: TypeAlias = dict[str, Any]
DatabaseData: TypeAlias = dict[str, Any]
Section: TypeAlias = Mapping[str, DatabaseData]
Fields: TypeAlias = dict[str, str]
CheckParams: TypeAlias = Mapping[str, Any]


def parse_json(string_table: StringTable) -> dict[str, DatabaseData]:
    result: dict[str, DatabaseData] = {}
    for row in string_table:
        try:
            obj = json.loads(" ".join(row))
        except (ValueError, TypeError):
            continue
        if (
            isinstance(obj, dict)
            and isinstance(obj.get("database"), str)
            and isinstance(obj.get("queries"), list)
        ):
            result[obj["database"]] = obj
    return result


def fields(obj: DatabaseData, name: str) -> Fields | None:
    for query in obj.get("queries", []):
        if query.get("query") == name:
            if query.get("status") != "ok":
                return None
            result: Fields = {}
            for line in query.get("output", "").splitlines():
                match = re.match(r"^\s*([A-Z][A-Z0-9_]*)\s*=\s*(.*?)\s*$", line)
                if match:
                    result[match.group(1)] = match.group(2).strip("\'\"")
            return result
    return None


def number(data: Mapping[str, str], key: str) -> float | None:
    try:
        return float(data[key])
    except (KeyError, TypeError, ValueError):
        return None


def discover_query(section: Section, query: str) -> DiscoveryResult:
    for database, obj in section.items():
        if fields(obj, query) is not None:
            yield Service(item=database)


def discover_backup(section: Section) -> DiscoveryResult:
    for database, obj in section.items():
        if any(
            q.get("query") == "backup_history" and q.get("status") == "ok"
            for q in obj.get("queries", [])
        ):
            yield Service(item=database)
