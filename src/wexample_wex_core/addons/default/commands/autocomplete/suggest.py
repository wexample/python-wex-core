from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON
from wexample_wex_core.decorator.command import command
from wexample_wex_core.decorator.option import option

if TYPE_CHECKING:
    from wexample_wex_core.context.execution_context import ExecutionContext

# TODO: Implement cursor-aware suggestions (addon names, groups, commands, args)
# cursor=0 → addon names, cursor=1 → groups, cursor=2 → commands, cursor≥3 → args


@option(name="search", short_name="s", type=str, required=False)
@option(name="cursor", short_name="c", type=int, required=False)
@command(
    type=COMMAND_TYPE_ADDON,
    description="Suggest autocomplete options for a partial wex command",
)
def default__autocomplete__suggest(
    context: ExecutionContext,
    search: str = "",
    cursor: int = 0,
) -> list:
    return []
