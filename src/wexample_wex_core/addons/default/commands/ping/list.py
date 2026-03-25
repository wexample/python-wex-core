from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON
from wexample_wex_core.decorator.command import command
from wexample_wex_core.response.list_response import ListResponse

if TYPE_CHECKING:
    from wexample_wex_core.context.execution_context import ExecutionContext


@command(type=COMMAND_TYPE_ADDON)
def default__ping__list(context: ExecutionContext) -> ListResponse:
    return ListResponse(kernel=context.kernel, content=["pong", "ping", "pang"])
