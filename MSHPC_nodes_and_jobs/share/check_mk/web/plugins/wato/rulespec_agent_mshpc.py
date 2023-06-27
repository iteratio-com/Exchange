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
                    default_value=_("https://zdeoko04sc4h2.zeiss.org/WindowsHpc/"),
                ),
            ),
            (
                "user",
                TextAscii(title="User", default_value=_("Y19MSHPC")),
            ),
            ("secret", IndividualOrStoredPassword(title="Secret")),
            # ("cert",
            #  Checkbox(title=_("Disable cert verification"),
            #           label=_("Disable cert verification"))),
        ],
        required_keys=["user", "url", "secret"],
    ),
    title=_("Check MSHPC Status"),
    help=_("This rule is used to set up an api endpoint for MSHPC api calls."),
    match="dict",
)
