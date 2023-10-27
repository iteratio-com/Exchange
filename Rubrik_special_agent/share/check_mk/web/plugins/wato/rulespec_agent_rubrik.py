#!/usr/bin/env python
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# 2023, marcus.klein@iteratio.com

from cmk.gui.plugins.wato.utils import IndividualOrStoredPassword
from cmk.gui.valuespec import Dictionary, TextInput, Checkbox

register_rule(
    "datasource_programs",
    "special_agents:rubrik",
    Dictionary(
        elements=[
            (
                "user",
                TextInput(title="User", default_value=_("User")),
            ),
            ("secret", IndividualOrStoredPassword(title="Secret")),
            (
                "verify_ssl",
                Checkbox(
                    title=_("Enable SSL certtificate verification"),
                    label=_("Enable verification"),
                ),
            ),
        ],
        required_keys=["user", "secret", "verify_ssl"],
    ),
    title=_("Rubrik Special Agent"),
    help=_("This rule is used to set up credentials for Rubrik api calls."),
    match="dict",
)
