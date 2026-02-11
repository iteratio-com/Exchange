#!/usr/bin/env python3

from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    Integer,
)
from cmk.rulesets.v1.rule_specs import (
    CheckParameters,
    Help,
    HostAndItemCondition,
    Title,
    Topic,
)


def _form_spec_rubrik_cluster_compliance_24_hours():  # noqa: ANN202
    def _migrate(value: object) -> dict[str, int]:
        def _extract_pair(raw: object, default_warn: int, default_crit: int) -> tuple[int, int]:
            warn, crit = default_warn, default_crit
            if isinstance(raw, dict):
                warn = raw.get("warn", raw.get("warning", warn))
                crit = raw.get("crit", raw.get("to", raw.get("critical", crit)))
            elif isinstance(raw, (list, tuple)):
                payload = raw[1] if len(raw) > 1 else None
                if isinstance(payload, dict):
                    warn = payload.get("warning", payload.get("warn", warn))
                    crit = payload.get("critical", payload.get("crit", payload.get("to", crit)))
                elif isinstance(payload, (list, tuple)):
                    if len(payload) > 0:
                        warn = payload[0]
                    if len(payload) > 1:
                        crit = payload[1]
            return int(warn), int(crit)

        if not isinstance(value, dict):
            return {}

        migrated: dict[str, int] = dict(value)
        abs_warn, abs_crit = _extract_pair(value.get("absolute_out_of_compliance"), 1, 5)
        migrated.setdefault("absolute_out_of_compliance_warn", abs_warn)
        migrated.setdefault("absolute_out_of_compliance_crit", abs_crit)
        migrated.pop("absolute_out_of_compliance", None)

        perc_warn, perc_crit = _extract_pair(value.get("percent_out_of_compliance"), 1, 5)
        migrated.setdefault("percent_out_of_compliance_warn", perc_warn)
        migrated.setdefault("percent_out_of_compliance_crit", perc_crit)
        migrated.pop("percent_out_of_compliance", None)

        return migrated

    return Dictionary(
        title=Title("Rubrik Compliance 24 Hours Snapshot Levels"),
        help_text=Help("Configure thresholds for Rubrik compliance monitoring"),
        migrate=_migrate,
        elements={
            "absolute_out_of_compliance_warn": DictElement(
                required=False,
                parameter_form=Integer(
                    title=Title("Warning level for snapshots out of compliance (absolute)"),
                    unit_symbol="snapshots",
                    prefill=DefaultValue(1),
                ),
            ),
            "absolute_out_of_compliance_crit": DictElement(
                required=False,
                parameter_form=Integer(
                    title=Title("Critical level for snapshots out of compliance (absolute)"),
                    unit_symbol="snapshots",
                    prefill=DefaultValue(5),
                ),
            ),
            "percent_out_of_compliance_warn": DictElement(
                required=False,
                parameter_form=Integer(
                    title=Title("Warning level for snapshots out of compliance (percentage)"),
                    unit_symbol="%",
                    prefill=DefaultValue(1),
                ),
            ),
            "percent_out_of_compliance_crit": DictElement(
                required=False,
                parameter_form=Integer(
                    title=Title("Critical level for snapshots out of compliance (percentage)"),
                    unit_symbol="%",
                    prefill=DefaultValue(5),
                ),
            ),
        },
    )


rule_spec_rubrik_cluster_compliance_24_hours = CheckParameters(
    name="rubrik_cluster_compliance_24_hours",
    topic=Topic.STORAGE,
    condition=HostAndItemCondition(item_title=Title("Service")),
    parameter_form=_form_spec_rubrik_cluster_compliance_24_hours,
    title=Title("Rubrik Compliance 24 Hours Snapshot Levels"),
)
