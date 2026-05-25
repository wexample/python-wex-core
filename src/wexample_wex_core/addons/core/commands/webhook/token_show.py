from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_cli.decorator.command import command
from wexample_cli.decorator.option import option

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON

if TYPE_CHECKING:
    from wexample_cli.context.execution_context import ExecutionContext

_VALID_TYPES = ("addon", "service")


@option(
    "type_name",
    type=str,
    required=True,
    description="Webhook type: addon or service",
)
@option(
    "command_name",
    type=str,
    required=True,
    description="Command whose token should be shown, e.g. 'app::info/show'",
)
@command(
    type=COMMAND_TYPE_ADDON,
    description="Show the webhook token for an addon or service command",
)
def core__webhook__token_show(
    context: ExecutionContext,
    type_name: str,
    command_name: str,
) -> None:
    if type_name not in _VALID_TYPES:
        context.io.error(f"--type must be one of: {', '.join(_VALID_TYPES)}")
        return

    token = context.kernel.workdir.get_local_data_value(
        f"webhook_tokens_{type_name}", command_name
    )
    if not token:
        context.io.warning(f"No token found for {command_name}.")
        return

    context.io.log(f"{command_name}:  @yellow{{{token}}}")
