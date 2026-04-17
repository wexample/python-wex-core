from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON
from wexample_wex_core.decorator.command import command

if TYPE_CHECKING:
    from wexample_wex_core.context.execution_context import ExecutionContext


@command(
    type=COMMAND_TYPE_ADDON,
    description="Check environment health: required env vars, and more checks over time",
)
def default__check__health(context: ExecutionContext) -> None:
    kernel = context.kernel
    io = context.io

    io.log(message="Health check")

    # --- Env vars ---
    expected_keys = kernel.get_expected_env_keys()
    if not expected_keys:
        io.success(message="Env vars: no required env vars declared")
    else:
        missing = kernel._get_missing_env_keys(expected_keys)
        if missing:
            io.error(
                message=f"Env vars: {len(missing)} missing: {', '.join(missing)}"
            )
        else:
            io.success(
                message=f"Env vars: all {len(expected_keys)} required var(s) present"
            )

    # --- SSH agent ---
    import os

    from wexample_helpers_git.service.ssh_agent_resolver import SshAgentResolver

    socket_path = SshAgentResolver().resolve()
    if socket_path:
        io.success(message=f"SSH agent: socket found at {socket_path}")
    else:
        sock_env = os.environ.get("SSH_AUTH_SOCK", "")
        if sock_env:
            io.warning(
                message=f"SSH agent: SSH_AUTH_SOCK set ({sock_env}) but socket not reachable"
            )
        else:
            io.warning(
                message=(
                    "SSH agent: no agent socket found. "
                    "Git push/pull via SSH may fail. "
                    "Fix: eval $(ssh-agent) && ssh-add"
                )
            )
