from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON
from wexample_wex_core.decorator.command import command
from wexample_wex_core.decorator.option import option

if TYPE_CHECKING:
    from wexample_wex_core.context.execution_context import ExecutionContext


@option(
    "command_name",
    type=str,
    required=True,
    description="Wex command whose token should be rotated (e.g. 'app::info/show')",
)
@command(
    type=COMMAND_TYPE_ADDON,
    description="Rotate (regenerate) the webhook token for a command",
)
def core__webhook__token_rotate(
    context: ExecutionContext,
    command_name: str,
) -> None:
    token = context.kernel.workdir.rotate_local_token("webhook_tokens", command_name)

    context.io.log(f"New webhook token for  {command_name}")
    context.io.log(token)
    context.io.warning("Old token is now invalid. Update any callers.")
