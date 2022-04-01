#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
from typing import Any, Dict, List

from .bakery_api.v1 import FileGenerator, OS, Plugin, register, PluginConfig


def bake_maxdb(conf: Any) -> FileGenerator:
    yield Plugin(base_os=OS.LINUX,
                 source=Path("maxdb.py"),
                 target=Path('maxdb'),
                 interval=conf.get('interval'))

    yield PluginConfig(base_os=OS.LINUX,
                       lines=_get_maxdb_conf_lines(conf),
                       target=Path("maxdb.cfg"),
                       include_header=True)


def _get_maxdb_conf_lines(conf: Dict[str, str]) -> List[str]:
    out = []
    for item in conf.get('databases'):
        db = [
            f"[{item.get('dbname')}]",
            f"user={item.get('user')}",
            f"password={item.get('password')}",
            "cmd_tool=" + item.get('cmd_tool', f'/sapdb/{item.get("dbname")}/db/bin/dbmcli'),
            f"timeout={item.get('timeout',20)}",
            f"modules={str(item.get('modules'))}",
        ]
        out.extend(db)
    return out


register.bakery_plugin(
    name="maxdb",
    files_function=bake_maxdb,
)
