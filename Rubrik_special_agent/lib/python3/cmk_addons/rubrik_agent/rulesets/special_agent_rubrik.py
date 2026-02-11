#!/usr/bin/env python3

from cmk.rulesets.v1 import Help, Label, Title
from cmk.rulesets.v1.form_specs import (
    BooleanChoice,
    DictElement,
    Dictionary,
    MultipleChoice,
    MultipleChoiceElement,
    Password,
    String,
    migrate_to_password,
)
from cmk.rulesets.v1.rule_specs import SpecialAgent, Topic


def _formspec() -> Dictionary:
    return Dictionary(
        title=Title("Rubrik Special Agent"),
        help_text=Help("This rule is used to set up Rubrik Special agent."),
        elements={
            "user": DictElement(
                required=True,
                parameter_form=String(
                    title=Title("User"),
                    help_text=Help("Username for Rubrik API authentication"),
                ),
            ),
            "secret": DictElement(
                required=True,
                parameter_form=Password(
                    title=Title("Secret of API user"),
                    help_text=Help("Password for Rubrik API authentication"),
                    migrate=migrate_to_password,
                ),
            ),
            "verify_ssl": DictElement(
                required=False,
                parameter_form=BooleanChoice(
                    title=Title("Enable SSL certificate verification"),
                    label=Label("Enable SSL certificate verification"),
                    help_text=Help("Enable SSL certificate verification for API calls"),
                ),
            ),
            "sections": DictElement(
                required=False,
                parameter_form=MultipleChoice(
                    title=Title("Sections"),
                    help_text=Help("Select the sections to be monitored, default are all sections."),
                    elements=[
                        MultipleChoiceElement(
                            name="cluster_system_status",
                            title=Title("Rubrik Cluster System Status"),
                        ),
                        MultipleChoiceElement(
                            name="cluster_compliance_status",
                            title=Title("Rubrik Cluster Report Compliance Status 24h"),
                        ),
                        MultipleChoiceElement(
                            name="node_status",
                            title=Title("Rubrik Node Status"),
                        ),
                        MultipleChoiceElement(
                            name="node_disk_status",
                            title=Title("Rubrik Node Disk Status"),
                        ),
                        MultipleChoiceElement(
                            name="node_hardware_health",
                            title=Title("Rubrik Node Hardware Health"),
                        ),
                    ],
                ),
            ),
        },
    )


rule_spec_rubrik = SpecialAgent(
    topic=Topic.STORAGE,
    name="rubrik",
    title=Title("Rubrik Special Agent"),
    parameter_form=_formspec,
)
