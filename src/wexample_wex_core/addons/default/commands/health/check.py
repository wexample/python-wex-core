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
def default__health__check(context: ExecutionContext) -> None:
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
            io.error(message=f"Env vars: {len(missing)} missing: {', '.join(missing)}")
        else:
            io.success(
                message=f"Env vars: all {len(expected_keys)} required var(s) present"
            )

    # --- SSH agent ---
    import os
    import stat

    sock = os.environ.get("SSH_AUTH_SOCK", "")
    if not sock:
        io.warning(
            message=(
                "SSH agent: SSH_AUTH_SOCK not set. "
                "Git push/pull via SSH may fail. "
                "Set it in .wex/local/env.yml or run: eval $(ssh-agent) && ssh-add"
            )
        )
    else:
        try:
            if stat.S_ISSOCK(os.stat(sock).st_mode):
                io.success(message=f"SSH agent: socket reachable at {sock}")
            else:
                io.warning(
                    message=f"SSH agent: SSH_AUTH_SOCK set but {sock} is not a socket"
                )
        except OSError:
            io.warning(
                message=f"SSH agent: SSH_AUTH_SOCK set but socket not found at {sock}"
            )
