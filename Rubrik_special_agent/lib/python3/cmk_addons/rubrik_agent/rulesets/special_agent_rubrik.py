#!/usr/bin/env python3

from cmk.rulesets.v1 import Help, Label, Title
from cmk.rulesets.v1.form_specs import (
    BooleanChoice,
    CascadingSingleChoice,
    CascadingSingleChoiceElement,
    DefaultValue,
    DictElement,
    Dictionary,
    MultipleChoice,
    MultipleChoiceElement,
    Password,
    String,
    migrate_to_password,
    Integer,
)
from cmk.rulesets.v1.rule_specs import SpecialAgent, Topic


def _migrate_special_agent_params(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        return {}

    migrated = dict(value)

    if "user" in migrated and "client_id" not in migrated:
        migrated["client_id"] = migrated.pop("user")
    else:
        migrated.pop("user", None)

    if "secret" in migrated and "client_secret" not in migrated:
        migrated["client_secret"] = migrated.pop("secret")
    else:
        migrated.pop("secret", None)

    if "cluster_selector" not in migrated:
        if migrated.get("cluster_uuid"):
            migrated["cluster_selector"] = ("cluster_uuid", str(migrated["cluster_uuid"]))
        elif migrated.get("cluster_name"):
            migrated["cluster_selector"] = ("cluster_name", str(migrated["cluster_name"]))

    migrated.pop("cluster_name", None)
    migrated.pop("cluster_uuid", None)

    if "disable_ssl_verification" not in migrated and "verify_ssl" in migrated:
        migrated["disable_ssl_verification"] = not bool(migrated.pop("verify_ssl"))
    else:
        migrated.pop("verify_ssl", None)

    return migrated


def _formspec() -> Dictionary:
    return Dictionary(
        title=Title("Rubrik Special Agent"),
        help_text=Help("This rule is used to set up Rubrik Special agent."),
        migrate=_migrate_special_agent_params,
        elements={
            "client_id": DictElement(
                required=True,
                parameter_form=String(
                    title=Title("RSC Client ID"),
                    help_text=Help("Client ID of the Rubrik Security Cloud service account"),
                ),
            ),
            "client_secret": DictElement(
                required=True,
                parameter_form=Password(
                    title=Title("RSC Client Secret"),
                    help_text=Help("Client secret of the Rubrik Security Cloud service account"),
                    migrate=migrate_to_password,
                ),
            ),
            "access_token_uri": DictElement(
                required=True,
                parameter_form=String(
                    title=Title("RSC Access Token URI"),
                    help_text=Help(
                        "Token endpoint of the Rubrik Security Cloud tenant, for example https://obi.my.rubrik.com/api/client_token"
                    ),
                ),
            ),
            "cluster_selector": DictElement(
                required=True,
                parameter_form=CascadingSingleChoice(
                    title=Title("Rubrik Cluster Selector"),
                    label=Label("Rubrik Cluster Selector"),
                    help_text=Help("Select whether the monitored Rubrik cluster is identified by name or UUID."),
                    elements=[
                        CascadingSingleChoiceElement(
                            name="cluster_name",
                            title=Title("Cluster Name"),
                            parameter_form=String(
                                title=Title("Rubrik Cluster Name"),
                                help_text=Help("Cluster name in RSC used to resolve the monitored cluster"),
                            ),
                        ),
                        CascadingSingleChoiceElement(
                            name="cluster_uuid",
                            title=Title("Cluster UUID"),
                            parameter_form=String(
                                title=Title("Rubrik Cluster UUID"),
                                help_text=Help("Cluster UUID in RSC used to resolve the monitored cluster"),
                            ),
                        ),
                        CascadingSingleChoiceElement(
                            name="saas",
                            title=Title("SAAS"),
                            parameter_form=BooleanChoice(
                                title=Title("SAAS instead of one cluster"),
                                label=Label("SAAS instead of one cluster"),
                                help_text=Help("SAAS instead of one cluster for RSC API calls."),
                                prefill=DefaultValue(False),
                            ),
                        ),
                    ],
                ),
            ),
            "disable_ssl_verification": DictElement(
                required=False,
                parameter_form=BooleanChoice(
                    title=Title("Disable SSL certificate verification"),
                    label=Label("Disable SSL certificate verification"),
                    help_text=Help("Disable SSL certificate verification for RSC API calls."),
                    prefill=DefaultValue(False),
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
                            name="bandwidth",
                            title=Title("Rubrik Cluster Bandwidth"),
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
                        MultipleChoiceElement(
                            name="cluster_event_logwatch",
                            title=Title("Rubrik Cluster Events Logwatch"),
                        ),
                    ],
                ),
            ),
            "event_filter_severity": DictElement(
                required=False,
                parameter_form=String(
                    title=Title("Event severity filter"),
                    help_text=Help("Event severity filter list as string, seperator is ','. For example values, please log in to the UI section, go to the Event page, and use the browser's network analysis to determine which filters are required."),
                ),
            ),
            "event_filter_last_activity_types": DictElement(
                required=False,
                parameter_form=String(
                    title=Title("Event activity types filter"),
                    help_text=Help("Event activity types filter list as string, seperator is ','.For example values, please log in to the UI section, go to the Event page, and use the browser's network analysis to determine which filters are required. "),
                ),
            ),
            "event_filter_last_activity_status": DictElement(
                required=False,
                parameter_form=String(
                    title=Title("Event activity status filter"),
                    help_text=Help("Event activity status filter list as string, seperator is ','. For example values, please log in to the UI section, go to the Event page, and use the browser's network analysis to determine which filters are required."),
                ),
            ),
            "event_filter_object_type": DictElement(
                required=False,
                parameter_form=String(
                    title=Title("Event object type filter"),
                    help_text=Help("Event object type filter list as string, seperator is ','. For example values, please log in to the UI section, go to the Event page, and use the browser's network analysis to determine which filters are required."),
                ),
            ),
            "timeout": DictElement(
                required=False,
                parameter_form=Integer(
                    title=Title("Timeout"),
                    help_text=Help("Timeout for each request"),
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
