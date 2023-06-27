#!/usr/bin/env python
# -*- encoding: utf-8; py-indent-offset: 4 -*-

from cmk.gui.plugins.wato.utils import IndividualOrStoredPassword
from cmk.gui.valuespec import TextAscii

register_rule(
    "datasource_programs",
    "special_agents:mshpc",
    Dictionary(
        elements=[
            (
                "url",
                HTTPUrl(
                    title=_("MSHPC API Url"),
                    default_value=_("https://mshpc.host.org/WindowsHpc/"),
                ),
            ),
            (
                "user",
                TextAscii(title="User", default_value=_("MSHPC")),
            ),
            ("secret", IndividualOrStoredPassword(title="Secret")),
        ],
        required_keys=["user", "url", "secret"],
    ),
    title=_("Check MSHPC Status"),
    help=_("This rule is used to set up an api endpoint for MSHPC api calls."),
    match="dict",
)
