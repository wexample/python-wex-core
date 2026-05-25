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
@command(
    type=COMMAND_TYPE_ADDON,
    description="List all webhook tokens for addon or service commands",
)
def core__webhook__token_list(
    context: ExecutionContext,
    type_name: str,
) -> None:
    if type_name not in _VALID_TYPES:
        context.io.error(f"--type must be one of: {', '.join(_VALID_TYPES)}")
        return

    tokens: dict = context.kernel.workdir.get_local_data(f"webhook_tokens_{type_name}")

    if not tokens:
        context.io.log(f"No webhook tokens registered for {type_name} commands.")
        return

    rows = [
        [cmd, f"@yellow{{{token[:8]}}}..."] for cmd, token in sorted(tokens.items())
    ]

    context.io.table(data=rows, headers=["Command", "Token (prefix)"])
