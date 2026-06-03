from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_cli.decorator.alias import alias
from wexample_cli.decorator.command import command

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON

if TYPE_CHECKING:
    from wexample_cli.context.execution_context import ExecutionContext


@alias("logo")
@command(type=COMMAND_TYPE_ADDON, description="Show the application logo")
def core__logo__show(context: ExecutionContext):
    from wexample_app.response.warning_response import WarningResponse

    logo = context.kernel.get_logo()

    if logo is None:
        return WarningResponse(
            kernel=context.kernel, message="No logo defined for this CLI."
        )

    return logo
