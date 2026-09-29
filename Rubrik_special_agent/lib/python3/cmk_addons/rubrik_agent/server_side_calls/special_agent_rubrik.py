#!/usr/bin/env python3

from collections.abc import Iterator

from cmk.server_side_calls.v1 import (
    HostConfig,
    Secret,
    SpecialAgentCommand,
    SpecialAgentConfig,
)
from pydantic import BaseModel


class RubrikParams(BaseModel):
    client_id: str
    client_secret: Secret
    access_token_uri: str
    cluster_selector: tuple[str, str] | tuple[str, bool] | None = None
    cluster_name: str | None = None
    cluster_uuid: str | None = None
    saas: bool | None = None
    event_filter_severity: str | None = None
    event_filter_last_activity_types: str | None = None
    event_filter_last_activity_status: str | None = None
    event_filter_object_type: str | None = None
    timeout: int | None = None
    disable_ssl_verification: bool | None = None
    verify_ssl: bool | None = None
    sections: list[str] | None = None


def _selector_arguments(params: RubrikParams) -> list[str]:
    if params.cluster_selector:
        selector_type, selector_value = params.cluster_selector
        if selector_type == "cluster_name":
            return ["--cluster-name", selector_value]
        if selector_type == "cluster_uuid":
            return ["--cluster-uuid", selector_value]
        if selector_type == "saas":
            return ["--saas"]

    if params.cluster_uuid:
        return ["--cluster-uuid", params.cluster_uuid]
    if params.cluster_name:
        return ["--cluster-name", params.cluster_name]
    if params.saas:
        return ["--saas"]

    return []


def _agent_arguments(params: RubrikParams, host_config: HostConfig) -> Iterator[SpecialAgentCommand]:
    """Generate command arguments for the Rubrik special agent."""
    args = [
        "--client-id",
        params.client_id,
        "--client-secret",
        params.client_secret,
        "--access-token-uri",
        params.access_token_uri,
        * _selector_arguments(params),
    ]

    if host_config.name:
        args.extend(["--hostname", host_config.name])

    if params.disable_ssl_verification is True or params.verify_ssl is False:
        args.append("--no-verify-ssl")
    else:
        args.append("--verify_ssl")

    if params.sections:
        args.extend(["--sections", ",".join(params.sections)])
    if params.event_filter_severity:
        args.extend(["--event-severity", params.event_filter_severity])
    if params.event_filter_last_activity_types:
        args.extend(["--event-lastactivitytype", params.event_filter_last_activity_types])
    if params.event_filter_last_activity_status:
        args.extend(["--event-lastactivitystatus", params.event_filter_last_activity_status])
    if params.event_filter_object_type:
        args.extend(["--event-objecttype", params.event_filter_object_type])
    if params.timeout:
        args.extend(["--timeout", str(params.timeout)])

    yield SpecialAgentCommand(command_arguments=args)


special_agent_rubrik = SpecialAgentConfig(
    name="rubrik",
    parameter_parser=RubrikParams.model_validate,
    commands_function=_agent_arguments,
)
