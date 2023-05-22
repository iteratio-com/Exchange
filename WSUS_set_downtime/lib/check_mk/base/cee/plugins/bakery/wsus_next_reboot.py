#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
from typing import Any

from .bakery_api.v1 import OS, FileGenerator, Plugin, register
from typing import Any, Dict


def get_wsus_next_reboot_files(conf: Dict[str, Any]) -> FileGenerator:
    yield Plugin(base_os=OS.WINDOWS, source=Path("wsus_next_reboot.ps1"))


register.bakery_plugin(
    name="wsus_next_reboot",
    files_function=get_wsus_next_reboot_files,
)
