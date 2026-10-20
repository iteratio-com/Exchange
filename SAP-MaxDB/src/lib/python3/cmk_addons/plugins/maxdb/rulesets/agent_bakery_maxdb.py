from collections.abc import Sequence
from typing import Literal

from cmk.rulesets.v1 import Help, Label, Message, Title
from cmk.rulesets.v1.form_specs import (
    CascadingSingleChoice,
    CascadingSingleChoiceElement,
    DefaultValue,
    DictElement,
    Dictionary,
    FixedValue,
    Integer,
    List,
    MultipleChoice,
    MultipleChoiceElement,
    Password,
    String,
    TimeMagnitude,
    TimeSpan,
    migrate_to_password,
    validators,
)
from cmk.rulesets.v1.rule_specs import AgentConfig, Topic


def migrate_elements(x: object) -> Sequence[str]:
    if isinstance(x, list):
        out = []
        for element in x:
            out.append(element.split(":")[0])
        return list(dict.fromkeys(out + ["locks", "performance", "volumes", "backup_extended", "transactions"]))
    else:
        return x


def migrate_our_password(
    x: object,
) -> tuple[
    Literal["cmk_postprocessed"], Literal["explicit_password", "stored_password"], tuple[str, str]
]:
    if isinstance(x, str):
        return migrate_to_password(("password", x))
    elif isinstance(x, tuple):
        return migrate_to_password(x)
    else:
        return migrate_to_password(x)


def migrate_authentication(value: object) -> object:
    # CascadingSingleChoice migration receives the existing choice value.
    if isinstance(value, tuple) and len(value) == 2:
        return value
    return value


def migrate_database(value: object) -> object:
    if not isinstance(value, dict) or "authentication" in value:
        return value
    result = dict(value)
    if result.get("xuser_key"):
        result["authentication"] = ("xuser_key", result.pop("xuser_key"))
        result.pop("user", None)
        result.pop("password", None)
    elif "user" in result or "password" in result:
        result["authentication"] = ("credentials", {
            "user": result.pop("user", ""),
            "password": result.pop("password", ""),
        })
    return result


def migrate_authentication(value: object) -> object:
    # CascadingSingleChoice migration receives the existing choice value.
    if isinstance(value, tuple) and len(value) == 2:
        return value
    return value


def migrate_database(value: object) -> object:
    if not isinstance(value, dict) or "authentication" in value:
        return value
    result = dict(value)
    if result.get("xuser_key"):
        result["authentication"] = ("xuser_key", result.pop("xuser_key"))
        result.pop("user", None)
        result.pop("password", None)
    elif "user" in result or "password" in result:
        result["authentication"] = ("credentials", {
            "user": result.pop("user", ""),
            "password": result.pop("password", ""),
        })
    return result


DATABASES_CONFIG = Dictionary(
    migrate=migrate_database,
    elements={
        "dbname": DictElement(
            required=False,
            parameter_form=String(
                title=Title("Name of Database"),
                help_text=Help(
                    "Name of the MaxDB, if not set it will try to determine the name by the path of dbmcli."
                    "It will look for paths like /sapdb/DBNAME/db/bin/dbmcli and use DBNAME as database name. "
                    "Excluded are DBAnalyze, clients, data, programs and the name must be 3 characters long."
                ),
            ),
        ),
        "authentication": DictElement(
            required=True,
            parameter_form=CascadingSingleChoice(
                title=Title("Authentication"),
                prefill=DefaultValue("xuser_key"),
                migrate=migrate_authentication,
                elements=(
                    CascadingSingleChoiceElement(
                        name="xuser_key",
                        title=Title("XUSER key"),
                        parameter_form=String(title=Title("XUSER key")),
                    ),
                    CascadingSingleChoiceElement(
                        name="credentials",
                        title=Title("Username and password"),
                        parameter_form=Dictionary(elements={
                            "user": DictElement(required=True, parameter_form=String(title=Title("Username"))),
                            "password": DictElement(required=True, parameter_form=Password(
                                title=Title("Password"), migrate=migrate_our_password,
                            )),
                        }),
                    ),
                ),
            ),
        ),
        "modules": DictElement(
            required=True,
            parameter_form=MultipleChoice(
                title=Title("Aviable Modules/Querys to execute"),
                help_text=Help(
                    "The individual queries can be selected here. It is recommended to select State and Data/log usage together."
                ),
                elements=[
                    MultipleChoiceElement(name="state", title=Title("Overall State of the DB")),
                    MultipleChoiceElement(name="backup", title=Title("Backup State")),
                    MultipleChoiceElement(name="data", title=Title("Data and Log usage")),
                    MultipleChoiceElement(name="locks", title=Title("Locks and deadlocks")),
                    MultipleChoiceElement(name="performance", title=Title("SQL performance")),
                    MultipleChoiceElement(name="volumes", title=Title("Data and log volumes")),
                    MultipleChoiceElement(name="backup_extended", title=Title("Extended backup monitoring")),
                    MultipleChoiceElement(name="transactions", title=Title("Transactions")),
                ],
                migrate=migrate_elements,
                prefill=DefaultValue(["state", "backup", "data", "locks", "performance", "volumes", "backup_extended", "transactions"]),
            ),
        ),
        "timeout": DictElement(
            parameter_form=Integer(
                title=Title("Execution Timeout for a single Query"),
                custom_validate=(validators.NumberInRange(min_value=1, max_value=500),),
                unit_symbol="seconds",
                prefill=DefaultValue(20),
            )
        ),
    }
)


def migrate_interval(x: object) -> tuple[str, object]:
    if isinstance(x, int):
        return ("cached", float(x))
    if isinstance(x, tuple):
        if x[0] == "cached":
            return ("cached", float(x[1]))
        else:
            return x
    else:
        return x


def _form_spec_agent_config_maxdb() -> Dictionary:
    return Dictionary(
        elements={
            "databases": DictElement(
                required=True,
                parameter_form=List(
                    title=Title("Specify here the MaxDB/s settings for the Agent Plugin"),
                    add_element_label=Label("Add MaxDB Connection"),
                    element_template=DATABASES_CONFIG,
                ),
            ),
            "interval": DictElement(
                parameter_form=CascadingSingleChoice(
                    title=Title("Synchronicity / caching"),
                    prefill=DefaultValue("uncached"),
                    migrate=migrate_interval,
                    elements=(
                        CascadingSingleChoiceElement(
                            name="uncached",
                            title=Title("Run synchronously"),
                            parameter_form=FixedValue(value=None),
                        ),
                        CascadingSingleChoiceElement(
                            name="cached",
                            title=Title("Run asynchronously"),
                            parameter_form=TimeSpan(
                                label=Label("Interval for collecting data"),
                                displayed_magnitudes=[
                                    TimeMagnitude.HOUR,
                                    TimeMagnitude.MINUTE,
                                    TimeMagnitude.SECOND,
                                ],
                                prefill=DefaultValue(300.0),
                            ),
                        ),
                    ),
                ),
            ),
        },
    )


rule_spec_maxdb = AgentConfig(
    name="maxdb",
    topic=Topic.APPLICATIONS,
    title=Title("Use MaxDB Agent Plugin"),
    parameter_form=_form_spec_agent_config_maxdb,
)
