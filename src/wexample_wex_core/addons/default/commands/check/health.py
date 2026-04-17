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
