#!/usr/bin/env python3

from ast import literal_eval
from typing import Any, Optional

from cmk.agent_based.v2 import StringTable

RubrikSection = dict[str, Any]
RubrikSectionDisk = list[RubrikSection]


def parse_rubrik_single(string_table: StringTable) -> Optional[RubrikSection]:
    """Parse single rubrik node section, tolerating duplicate entries from multiple piggyback sources."""
    last_valid: RubrikSection = {}
    for entry in string_table:
        if not entry:
            continue
        try:
            parsed = literal_eval(entry[0])
        except Exception:
            continue
        if isinstance(parsed, dict):
            last_valid = parsed

    return last_valid


def parse_rubrik_list(string_table: StringTable) -> Optional[RubrikSectionDisk]:
    """Parse rubrik disk list section"""
    try:
        out = []
        for line in string_table:
            out.append(literal_eval(line[0]))
        return out
    except Exception:
        return []


# Backward compatibility
def parse_rubrik(string_table: StringTable) -> Optional[RubrikSection | RubrikSectionDisk]:
    """Legacy parse function - try to determine format automatically"""
    single = parse_rubrik_single(string_table)
    if single:
        return single

    try:
        return [literal_eval(line[0]) for line in string_table]
    except Exception:
        return {}
