#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cmk.gui.i18n import _
from cmk.gui.valuespec import (
    Dictionary,
    Integer,
    Tuple,
)

from cmk.gui.plugins.wato import (
    rulespec_registry,
    RulespecGroupCheckParametersApplications,
    CheckParameterRulespecWithoutItem,
)


def _valuespec_mshpc_jobs():
    return Dictionary(
        elements=[
            (
                "jobs_canceled",
                Dictionary(
                    title=_("Canceled Jobs"),
                    elements=[
                        (
                            "upper",
                            Tuple(
                                title=_("Upper limits"),
                                help=_("Upper levels for # of canceled jobs."),
                                elements=[
                                    Integer(title=_("Warning at")),
                                    Integer(title=_("Critical at")),
                                ],
                            ),
                        ),
                        (
                            "lower",
                            Tuple(
                                title=_("Lower limits"),
                                help=_("Lower levels for # of canceled jobs."),
                                elements=[
                                    Integer(title=_("Warning below")),
                                    Integer(title=_("Critical below")),
                                ],
                            ),
                        ),
                    ],
                ),
            ),
            (
                "jobs_configuring",
                Dictionary(
                    title=_("Configuring Jobs"),
                    elements=[
                        (
                            "upper",
                            Tuple(
                                title=_("Upper limits"),
                                help=_("Upper levels for # of configuring jobs."),
                                elements=[
                                    Integer(title=_("Warning at")),
                                    Integer(title=_("Critical at")),
                                ],
                            ),
                        ),
                        (
                            "lower",
                            Tuple(
                                title=_("Lower limits"),
                                help=_("Lower levels for # of configuring jobs."),
                                elements=[
                                    Integer(title=_("Warning below")),
                                    Integer(title=_("Critical below")),
                                ],
                            ),
                        ),
                    ],
                ),
            ),
            (
                "jobs_failed",
                Dictionary(
                    title=_("Failed Jobs"),
                    elements=[
                        (
                            "upper",
                            Tuple(
                                title=_("Upper limits"),
                                help=_("Upper levels for # of failed jobs."),
                                elements=[
                                    Integer(title=_("Warning at")),
                                    Integer(title=_("Critical at")),
                                ],
                            ),
                        ),
                        (
                            "lower",
                            Tuple(
                                title=_("Lower limits"),
                                help=_("Lower levels for # of failed jobs."),
                                elements=[
                                    Integer(title=_("Warning below")),
                                    Integer(title=_("Critical below")),
                                ],
                            ),
                        ),
                    ],
                ),
            ),
            (
                "jobs_queued",
                Dictionary(
                    title=_("Queued Jobs"),
                    elements=[
                        (
                            "upper",
                            Tuple(
                                title=_("Upper limits"),
                                help=_("Upper levels for # of queued jobs."),
                                elements=[
                                    Integer(title=_("Warning at")),
                                    Integer(title=_("Critical at")),
                                ],
                            ),
                        ),
                        (
                            "lower",
                            Tuple(
                                title=_("Lower limits"),
                                help=_("Lower levels for # of queued jobs."),
                                elements=[
                                    Integer(title=_("Warning below")),
                                    Integer(title=_("Critical below")),
                                ],
                            ),
                        ),
                    ],
                ),
            ),
            (
                "jobs_running",
                Dictionary(
                    title=_("Running Jobs"),
                    elements=[
                        (
                            "upper",
                            Tuple(
                                title=_("Upper limits"),
                                help=_("Upper levels for # of running jobs."),
                                elements=[
                                    Integer(title=_("Warning at")),
                                    Integer(title=_("Critical at")),
                                ],
                            ),
                        ),
                        (
                            "lower",
                            Tuple(
                                title=_("Lower limits"),
                                help=_("Lower levels for # of running jobs."),
                                elements=[
                                    Integer(title=_("Warning below")),
                                    Integer(title=_("Critical below")),
                                ],
                            ),
                        ),
                    ],
                ),
            ),
        ]
    )


rulespec_registry.register(
    CheckParameterRulespecWithoutItem(
        check_group_name="mshpc_jobs",
        group=RulespecGroupCheckParametersApplications,
        parameter_valuespec=_valuespec_mshpc_jobs,
        title=lambda: _("MSHPC Jobs"),
        match_type="dict",
        # item_spec=lambda: TextUnicode(title=_('Service name'), ),
    )
)
