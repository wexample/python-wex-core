from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON
from wexample_wex_core.decorator.command import command
from wexample_wex_core.decorator.option import option

if TYPE_CHECKING:
    from wexample_wex_core.context.execution_context import ExecutionContext


@option("command_name", type=str, required=True, description="Wex command to show/generate a token for (e.g. 'app::info/show')")
@command(type=COMMAND_TYPE_ADDON, description="Show (or generate) the webhook token for a command")
def default__webhook__token_show(
    context: ExecutionContext,
    command_name: str,
) -> None:
    from wexample_wex_core.webhook.token_store import token_store_ensure

    workdir_path = str(context.kernel.workdir.get_path())
    token = token_store_ensure(workdir_path, command_name)

    context.io.log(f"Webhook token for  {command_name}")
    context.io.log(token)
