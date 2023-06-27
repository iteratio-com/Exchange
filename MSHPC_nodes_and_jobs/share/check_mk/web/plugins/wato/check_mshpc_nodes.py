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


def _valuespec_mshpc_nodes():
    return Dictionary(
        elements=[
            (
                "nodes_online",
                Dictionary(
                    title=_("Online nodes"),
                    elements=[
                        (
                            "upper",
                            Tuple(
                                title=_("Upper limits"),
                                help=_("Upper levels for online nodes."),
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
                                help=_("Lower levels for online nodes."),
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
                "nodes_offline",
                Dictionary(
                    title=_("Offline nodes"),
                    elements=[
                        (
                            "upper",
                            Tuple(
                                title=_("Upper limits"),
                                help=_("Upper levels for offline nodes."),
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
                                help=_("Lower levels for offline nodes."),
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
                "nodes_draining",
                Dictionary(
                    title=_("Draining nodes"),
                    elements=[
                        (
                            "upper",
                            Tuple(
                                title=_("Upper limits"),
                                help=_("Upper levels for draining nodes."),
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
                                help=_("Lower levels for draining nodes."),
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
                "nodes_reachable",
                Tuple(
                    title=_("Reachable nodes"),
                    help=_("Lower levels for reachable nodes."),
                    elements=[
                        Integer(
                            title=_("Warning below"), minvalue=0, unit=_("Nodes"), default_value=10
                        ),
                        Integer(
                            title=_("Critical below"), minvalue=0, unit=_("Nodes"), default_value=5
                        ),
                    ],
                ),
            ),
            (
                "nodes_unreachable",
                Tuple(
                    title=_("Unreachable nodes"),
                    help=_("Upper levels for unreachable nodes."),
                    elements=[
                        Integer(
                            title=_("Warning at"), minvalue=0, unit=_("Nodes"), default_value=1
                        ),
                        Integer(
                            title=_("Critical at"), minvalue=0, unit=_("Nodes"), default_value=5
                        ),
                    ],
                ),
            ),
        ]
    )


rulespec_registry.register(
    CheckParameterRulespecWithoutItem(
        check_group_name="mshpc_nodes",
        group=RulespecGroupCheckParametersApplications,
        parameter_valuespec=_valuespec_mshpc_nodes,
        title=lambda: _("MSHPC Nodes"),
        match_type="dict",
        # item_spec=lambda: TextUnicode(title=_('Service name'), ),
    )
)
