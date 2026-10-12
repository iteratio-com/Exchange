"""Monitor Rubrik hardware health with configurable policy exceptions."""

from collections.abc import Mapping
from typing import Any

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    State,
)

from .utils.rubrik_api import RubrikSection, parse_rubrik_single


agent_section_rubrik_node_hardware_health = AgentSection(
    name="rubrik_node_hardware_health",
    parse_function=parse_rubrik_single,
)


def discover_node_hardware_health(section: RubrikSection) -> DiscoveryResult:
    """Discover one hardware health service per node."""
    if section:
        yield Service()


def check_node_hardware_health(params: Mapping[str, Any], section: RubrikSection) -> CheckResult:
    """Evaluate policies while preserving original findings in the details."""
    if not section:
        return

    policies = section.get("policies") or []
    if not policies:
        yield Result(state=State.UNKNOWN, summary="No hardware health policies returned")
        return

    overrides: dict[str, str] = {
        entry["policy_name"]: entry["handling"]
        for entry in params.get("policy_overrides", [])
    }
    states = {"ok": State.OK, "warn": State.WARN, "crit": State.CRIT}
    state = State.OK
    healthy = unhealthy = ignored = 0
    mapped: dict[str, int] = {}
    details = []
    for policy in policies:
        policy_name = policy.get("policyName") or "unknown policy"
        is_healthy = policy.get("isHealthy", True)
        line = f"{policy_name}: {'healthy' if is_healthy else 'unhealthy'}"
        if not is_healthy and policy.get("message"):
            line += f" - {policy['message']}"
        if is_healthy:
            healthy += 1
        elif (handling := overrides.get(policy_name, "crit")) == "ignore":
            ignored += 1
            line += " [ignored]"
        else:
            unhealthy += 1
            policy_state = states.get(handling, State.CRIT)
            state = State.worst(state, policy_state)
            if policy_name in overrides and handling in states:
                line += f" [mapped to {policy_state.name}]"
                mapped[policy_state.name] = mapped.get(policy_state.name, 0) + 1
        details.append(line)

    if ignored == len(policies):
        summary = "All hardware health policies are ignored"
    else:
        summary = (
            f"{healthy} hardware health policies are healthy"
            if not unhealthy
            else f"{unhealthy} hardware health policies are not healthy"
        )
        annotations = [f"{count} mapped to {name}" for name, count in mapped.items()]
        if ignored:
            annotations.append(f"{ignored} ignored")
        if annotations:
            summary += f" ({', '.join(annotations)})"

    yield Result(
        state=state,
        summary=summary,
        details="\n".join(details),
    )


check_plugin_rubrik_node_hardware_health = CheckPlugin(
    name="rubrik_node_hardware_health",
    service_name="Rubrik Node Hardware Health",
    discovery_function=discover_node_hardware_health,
    check_function=check_node_hardware_health,
    check_ruleset_name="rubrik_node_hardware_status",
    check_default_parameters={
        "percent_ssd_life_left": (50, 10),
        "policy_overrides": [],
    },
)
