#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

from ast import literal_eval
from typing import Any, Dict, List, Optional

from cmk.agent_based.v2 import StringTable

RubrikSection = Dict[str, Any]
RubrikSectionDisk = List[RubrikSection]


def parse_rubrik_single(string_table: StringTable) -> Optional[RubrikSection]:
    """Parse single rubrik node section"""
    try:
        out = literal_eval("".join([i[0] for i in string_table]))
        return out if isinstance(out, dict) else {}
    except Exception:
        return {}


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
    try:
        out = literal_eval("".join([i[0] for i in string_table]))
    except Exception:
        out = {}
    return out
