from cmk.agent_based.v2 import CheckPlugin, CheckResult, DiscoveryResult
from cmk_addons.plugins.maxdb.lib.backup import check_backup
from cmk_addons.plugins.maxdb.lib.common import CheckParams, Section, discover_backup, parse_json


def discover(section: Section) -> DiscoveryResult:
    yield from discover_backup(section)


def check(item: str, params: CheckParams, section: Section) -> CheckResult:
    yield from check_backup(item, params, section, "DAT", "Data backup")


# AgentSection is registered once in maxdb_log_backup.py; both plugins use it.
check_plugin_maxdb_data_backup = CheckPlugin(
    name="maxdb_data_backup",
    service_name="MaxDB %s Data Backup",
    sections=["maxdb_backup_extended"],
    discovery_function=discover,
    check_function=check,
    check_ruleset_name="maxdb_data_backup",
    check_default_parameters={"age": ("fixed", (172800.0, 259200.0)), "failed_state": 1},
)
