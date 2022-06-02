#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cmk.gui.i18n import _
from cmk.gui.valuespec import (
    Dictionary,
    MonitoringState,
    TextAscii,
)

from cmk.gui.plugins.wato import (
    CheckParameterRulespecWithItem,
    rulespec_registry,
    RulespecGroupCheckParametersApplications,
)


def _parameter_valuespec_dell_emc_ml3_drive():
    return Dictionary(elements=[
        ("cleaning_needed",
         MonitoringState(title=_("Status when Device cleaning needed"),
                         default_value=1)),
        ("ava_map",
         Dictionary(
             title=_("Avaible Status translation"),
             elements=[
                 ("1", MonitoringState(title=_("other"), default_value=1)),
                 ("2", MonitoringState(title=_("unknown"), default_value=3)),
                 ("3",
                  MonitoringState(title=_("runningFullPower"),
                                  default_value=0)),
                 ("4", MonitoringState(title=_("warning"), default_value=1)),
                 ("5", MonitoringState(title=_("inTest"), default_value=1)),
                 ("6",
                  MonitoringState(title=_("notApplicable"), default_value=1)),
                 ("7", MonitoringState(title=_("powerOff"), default_value=2)),
                 ("8", MonitoringState(title=_("offLine"), default_value=2)),
                 ("9", MonitoringState(title=_("offDuty"), default_value=1)),
                 ("10", MonitoringState(title=_("degraded"), default_value=2)),
                 ("11",
                  MonitoringState(title=_("notInstalled"), default_value=1)),
                 ("12",
                  MonitoringState(title=_("installError"), default_value=2)),
                 ("13",
                  MonitoringState(title=_("powerSaveUnknown"),
                                  default_value=1)),
                 ("14",
                  MonitoringState(title=_("powerSaveLowPowerMode"),
                                  default_value=1)),
                 ("15",
                  MonitoringState(title=_("powerSaveStandby"),
                                  default_value=1)),
                 ("16", MonitoringState(title=_("powerCycle"),
                                        default_value=1)),
                 ("17",
                  MonitoringState(title=_("powerSaveWarning"),
                                  default_value=1)),
                 ("18", MonitoringState(title=_("paused"), default_value=1)),
                 ("19", MonitoringState(title=_("notReady"), default_value=1)),
                 ("20",
                  MonitoringState(title=_("notConfigured"), default_value=1)),
                 ("21", MonitoringState(title=_("quiesced"), default_value=1)),
             ],
             optional_keys=[])),
        ("opa_map",
         Dictionary(
             title=_("Operational Status translation"),
             elements=[
                 ("0", MonitoringState(title=_("unknown"), default_value=3)),
                 ("1", MonitoringState(title=_("other"), default_value=1)),
                 ("2", MonitoringState(title=_("ok"), default_value=0)),
                 ("3", MonitoringState(title=_("degraded"), default_value=1)),
                 ("4", MonitoringState(title=_("stressed"), default_value=1)),
                 ("5",
                  MonitoringState(title=_("predictiveFailure"),
                                  default_value=1)),
                 ("6", MonitoringState(title=_("error"), default_value=2)),
                 ("7",
                  MonitoringState(title=_("non-RecoverableError"),
                                  default_value=2)),
                 ("8", MonitoringState(title=_("starting"), default_value=1)),
                 ("9", MonitoringState(title=_("stopping"), default_value=1)),
                 ("10", MonitoringState(title=_("stopped"), default_value=1)),
                 ("11", MonitoringState(title=_("inService"),
                                        default_value=1)),
                 ("12", MonitoringState(title=_("noContact"),
                                        default_value=2)),
                 ("13",
                  MonitoringState(title=_("lostCommunication"),
                                  default_value=1)),
                 ("14", MonitoringState(title=_("aborted"), default_value=1)),
                 ("15", MonitoringState(title=_("dormant"), default_value=1)),
                 ("16",
                  MonitoringState(title=_("supportingEntityInError"),
                                  default_value=2)),
                 ("17", MonitoringState(title=_("completed"),
                                        default_value=0)),
                 ("18", MonitoringState(title=_("powerMode"),
                                        default_value=1)),
                 ("19",
                  MonitoringState(title=_("dMTFReserved"), default_value=1)),
             ],
             optional_keys=[]))
    ], )


rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name="dell_emc_ml3_drive",
        group=RulespecGroupCheckParametersApplications,
        item_spec=lambda: TextAscii(title=_("Tape Drive"), ),
        match_type="dict",
        parameter_valuespec=_parameter_valuespec_dell_emc_ml3_drive,
        title=lambda: _("TapeLibrary Dell/EMC ML3 Status"),
    ))
