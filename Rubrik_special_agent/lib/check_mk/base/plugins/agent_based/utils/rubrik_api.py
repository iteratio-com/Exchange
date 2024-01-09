#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

from ast import literal_eval
from ..agent_based_api.v1.type_defs import StringTable
from typing import Dict, Any, Optional, List

RubrikSection = Dict[str, Any]
RubrikSectionDisk = List[RubrikSection]


def parse_rubrik(string_table: StringTable) -> Optional[RubrikSection | RubrikSectionDisk]:
    try:
        out = literal_eval("".join([i[0] for i in string_table]))
    except:
        out = {}
    return out
