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
    user: str
    secret: Secret
    verify_ssl: bool | None = None
    sections: list[str] | None = None


def _agent_arguments(params: RubrikParams, host_config: HostConfig) -> Iterator[SpecialAgentCommand]:
    """Generate command arguments for the Rubrik special agent."""
    args = [
        "--user",
        params.user,
        "--secret",
        params.secret.unsafe(),
        "--hostname",
        host_config.name,
    ]

    if params.verify_ssl:
        args.append("--verify_ssl")

    if params.sections:
        args.extend(["--sections", ",".join(params.sections)])

    yield SpecialAgentCommand(command_arguments=args)


# Define the special agent configuration using SpecialAgentConfig.
special_agent_rubrik = SpecialAgentConfig(
    name="rubrik",
    parameter_parser=RubrikParams.model_validate,
    commands_function=_agent_arguments,
)
