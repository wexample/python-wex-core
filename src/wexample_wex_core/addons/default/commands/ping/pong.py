from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON
from wexample_wex_core.decorator.command import command
from wexample_wex_core.response.dict_response import DictResponse

if TYPE_CHECKING:
    from wexample_wex_core.context.execution_context import ExecutionContext


@command(type=COMMAND_TYPE_ADDON)
def default__ping__pong(context: ExecutionContext) -> DictResponse:
    return DictResponse(kernel=context.kernel, content={"status": "pong"})
