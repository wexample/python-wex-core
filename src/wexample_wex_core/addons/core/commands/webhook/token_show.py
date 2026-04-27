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
    description="Wex command to show/generate a token for (e.g. 'app::info/show')",
)
@command(
    type=COMMAND_TYPE_ADDON,
    description="Show (or generate) the webhook token for a command",
)
def core__webhook__token_show(
    context: ExecutionContext,
    command_name: str,
) -> None:
    token = context.kernel.workdir.ensure_local_token("webhook_tokens", command_name)

    context.io.log(f"Webhook token for  {command_name}")
    context.io.log(token)
