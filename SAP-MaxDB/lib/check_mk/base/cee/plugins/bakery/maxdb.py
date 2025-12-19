#!/usr/bin/env python3

from pathlib import Path
from typing import Any

from cmk.base.plugins.bakery.bakery_api.v1 import (
    OS,
    FileGenerator,
    Plugin,
    PluginConfig,
    register,
)


def bake_maxdb(conf: Any) -> FileGenerator:
    if conf:
        caching, interval = conf.get("interval", ("uncached", None))

        yield Plugin(
            base_os=OS.LINUX,
            source=Path("maxdb.py"),
            target=Path("maxdb"),
            interval=int(interval) if caching == "cached" else None,
        )

        yield PluginConfig(
            base_os=OS.LINUX,
            lines=_get_maxdb_conf_lines(conf),
            target=Path("maxdb.cfg"),
            include_header=True,
        )


def _get_maxdb_conf_lines(conf: dict[str, str]) -> list[str]:
    out = []
    for item in conf.get("databases"):
        modules = [
            i.replace("backup", "backup:sep(124)").replace("data", "data:sep(61)")
            for i in item.get("modules", [])
        ]
        db = [
            f"[{item.get('dbname')}]",
            f"user={item.get('user')}",
            f"password={item.get('password')}",
            "cmd_tool=" + item.get("cmd_tool", f"/sapdb/{item.get('dbname')}/db/bin/dbmcli"),
            f"timeout={item.get('timeout', 20)}",
            f"modules={str(modules)}",
        ]
        out.extend(db)
    return out


register.bakery_plugin(
    name="maxdb",
    files_function=bake_maxdb,
)
