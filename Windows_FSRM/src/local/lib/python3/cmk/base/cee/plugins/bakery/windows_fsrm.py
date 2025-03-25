#!/usr/bin/env python3


from pathlib import Path
from typing import Any

from .bakery_api.v1 import FileGenerator, OS, Plugin, register


def bake_windows_fsrm(conf: Any) -> FileGenerator:
    if conf:
        yield Plugin(
            base_os=OS.WINDOWS,
            source=Path("win_fsrmquota.ps1"),
            interval=conf.get("interval"),
        )


register.bakery_plugin(
    name="windows_fsrm",
    files_function=bake_windows_fsrm,
)
