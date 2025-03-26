#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cmk.gui.valuespec import Dictionary, Tuple, Integer, MonitoringState, Percentage, Age , TextAscii
from cmk.gui.i18n import _
from cmk.gui.plugins.wato.utils import CheckParameterRulespecWithItem, rulespec_registry,RulespecGroupCheckParametersEnvironment,Levels

cpu = Dictionary(
    title=_("CPU Utilization"),
    help=_("This rule configures levels for the CPU utilization (not load) for "
           "Linux/UNIX, Windows and VMWare ESX host systems, as well as devices "
           "implementing the Host Resources MIB. The utilization "
           "percentage is computed with respect to the total number of CPUs. "
           "Note that not all parameters you can configure here are applicable "
           "to all checks."),
    elements=[
        ("core_util_time_total",
         Tuple(
             title=_("Levels over an extended time period on total CPU utilization"),
             elements=[
                 Percentage(title=_("High utilization at "), default_value=100.0),
                 Age(title=_("Warning after "), default_value=5 * 60),
                 Age(title=_("Critical after "), default_value=15 * 60),
             ],
             help=
             _("With this configuration, check_mk will alert if the actual (not averaged) total CPU is "
               "exceeding a utilization threshold over an extended period of time. "
               "ATTENTION: This configuration cannot be used for check <i>lparstat_aix.cpu_util</i>!"
              ))),
        ("average",
         Integer(
             title=_("Averaging for total CPU utilization"),
             help=_(
                 "When this option is activated then the CPU utilization is being "
                 "averaged <b>before</b> the levels on total CPU utilization are being applied."),
             unit=_("minutes"),
             minvalue=1,
             default_value=15,
             label=_("Compute average over last "),
         )),
        ("util",
         Levels(
             title=_("Levels on total CPU utilization"),
             unit="%",
             default_levels=(90, 95),
             default_difference=(5, 8),
             default_value=None,
             help=_(
                 "The CPU utilization sums up the percentages of CPU time that is used "
                 "for user processes, kernel routines (system), disk wait (sometimes also "
                 "called IO wait) or nothing (idle). The levels are always applied "
                 "on the average utilization since the last check - which is usually one minute."),
         )),
    ],
)

def _parameter_valuespec_fortigate_firewall_aps():
    return Dictionary(elements=[
        ("admin_state",
         Dictionary(elements=[
             ("0", MonitoringState(title=_("Status: Other"), default_value=3)),
             ("1", MonitoringState(title=_("Status: Discovered"), default_value=1)),
             ("2", MonitoringState(title=_("Status: Disable"), default_value=1)),
             ("3", MonitoringState(title=_("Status: Enable"), default_value=0)),
         ],optional_keys=[],title=_("Administrative state Mapping"),)),
        ("availability",
         Dictionary(elements=[
             ("0", MonitoringState(title=_("Status: Other"), default_value=3)),
             ("1", MonitoringState(title=_("Status: Offline"), default_value=2)),
             ("2", MonitoringState(title=_("Status: Online"), default_value=0)),
             ("3", MonitoringState(title=_("Status: Downloading Image"), default_value=0)),
             ("4", MonitoringState(title=_("Status: Connected Image"), default_value=0)),
         ], optional_keys=[],title=_("Availability Mapping"))),
        ('cpu_util', cpu),
        ('mem_usage',
         Tuple(title=_("Levels on memory utilization"),
               help=_("Set here the levels on memory utilization."),
               elements=[Percentage(title=_("WARNING at")),
                         Percentage(title=_("CRITICAL at"))])),
        ('in_rate',
         Tuple(
             title=_("Levels on Input Bandwith"),
             help=_("Set here the levels Input Bandwith, in Bytes per secound."),
             elements=[Integer(title=_("WARNING at"), unit="B/s"),
                       Integer(title=_("CRITICAL at"), unit="B/s")])),
        ('out_rate',
         Tuple(
             title=_("Levels on Output Bandwith"),
             help=_("Set here the levels Input Bandwith, out Bytes per secound."),
             elements=[Integer(title=_("WARNING at"), unit="B/s"),
                       Integer(title=_("CRITICAL at"), unit="B/s")])),
    ],
                      title=_("Fortigate Firewall AP Monitoring"),
                      optional_keys=[
                          'admin_state', 'availability', 'cpu_util', 'in_rate', 'out_rate',
                          'mem_usage'
                      ])


rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name="fortigate_firewall_aps",
        group=RulespecGroupCheckParametersEnvironment,
        match_type="dict",
        item_spec=lambda: TextAscii(title=_("Access Point")),
        parameter_valuespec=_parameter_valuespec_fortigate_firewall_aps,
        title=lambda: _("Fortigate Firewall AP Monitoring"),
    ))
