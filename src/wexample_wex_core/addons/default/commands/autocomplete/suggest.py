from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON
from wexample_wex_core.decorator.command import command
from wexample_wex_core.decorator.option import option

if TYPE_CHECKING:
    from wexample_app.response.abstract_response import AbstractResponse
    from wexample_wex_core.context.execution_context import ExecutionContext


@option(name="search", short_name="s", type=str, required=True, description="Partial input to complete")
@option(name="cursor", short_name="c", type=int, required=False, description="0-based index of the word being completed")
@command(type=COMMAND_TYPE_ADDON, description="Return suggestions for autocomplete")
def default__autocomplete__suggest(context: ExecutionContext, search: str, cursor: int = 0) -> AbstractResponse:
    from wexample_app.response.str_response import StrResponse

    search_split = search.split(" ") if search.strip() else [""]

    if cursor >= len(search_split):
        return StrResponse(kernel=context.kernel, content="")

    prefix = search_split[cursor]
    suggestions = context.kernel.get_configuration_registry().suggest(prefix)

    return StrResponse(kernel=context.kernel, content=" ".join(suggestions))
