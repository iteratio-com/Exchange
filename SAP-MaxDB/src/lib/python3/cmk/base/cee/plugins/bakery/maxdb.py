#!/usr/bin/env python3
import json
from pathlib import Path
from typing import Any

from cmk.base.plugins.bakery.bakery_api.v1 import OS, FileGenerator, Plugin, PluginConfig, register
from cmk.utils.password_store import lookup_for_bakery


def resolve_password(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, tuple) and len(value) == 3:
        _, kind, payload = value
        if kind == "explicit_password":
            return payload[1]
        if kind == "stored_password":
            return lookup_for_bakery(payload[0])
    if isinstance(value, tuple) and len(value) == 2:
        kind, secret = value
        return secret if kind == "password" else lookup_for_bakery(secret)
    raise ValueError("Invalid MaxDB password configuration")


def config_lines(conf: dict[str, Any]) -> list[str]:
    entries = []
    for item in conf.get("databases", []):
        entry = {
            "dbname": item.get("dbname", ""),
            "modules": [
                str(x).split(":")[0]
                for x in item.get(
                    "modules",
                    [
                        "state",
                        "backup",
                        "data",
                        "locks",
                        "performance",
                        "volumes",
                        "backup_extended",
                        "transactions",
                    ],
                )
            ],
            "timeout": item.get("timeout", 20),
        }
        authentication = item.get("authentication")
        if authentication is not None:
            mode, settings = authentication
            if mode == "xuser_key":
                entry["auth"] = {"xuser_key": settings}
            elif mode == "credentials":
                entry["auth"] = {
                    "user": settings["user"],
                    "password": resolve_password(settings["password"]),
                }
            else:
                raise ValueError(f"Unsupported MaxDB authentication mode: {mode}")
        elif item.get("xuser_key"):
            entry["auth"] = {"xuser_key": item["xuser_key"]}
        else:
            entry["auth"] = {
                "user": item.get("user", ""),
                "password": resolve_password(item["password"]),
            }
        entries.append(entry)
    return json.dumps({"databases": entries}, indent=2).splitlines()


def bake_maxdb(conf: dict[str, Any]) -> FileGenerator:
    if not conf:
        return
    caching, interval = conf.get("interval", ("uncached", None))
    for os_type in (OS.LINUX, OS.WINDOWS):
        yield Plugin(
            base_os=os_type,
            source=Path("maxdb.py"),
            target=Path("maxdb.py"),
            interval=int(interval) if caching == "cached" else None,
        )
        yield PluginConfig(
            base_os=os_type,
            lines=config_lines(conf),
            target=Path("maxdb.json"),
            include_header=False,
        )


register.bakery_plugin(name="maxdb", files_function=bake_maxdb)
