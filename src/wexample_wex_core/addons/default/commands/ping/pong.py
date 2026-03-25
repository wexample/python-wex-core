from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON
from wexample_wex_core.decorator.command import command
from wexample_wex_core.decorator.option import option

if TYPE_CHECKING:
    from wexample_app.response.abstract_response import AbstractResponse
    from wexample_wex_core.context.execution_context import ExecutionContext

PING_TYPE_DICT = "dict"
PING_TYPE_LIST = "list"


@option(name="type", type=str, required=True, description="Response type to return (dict, list)")
@command(type=COMMAND_TYPE_ADDON)
def default__ping__pong(context: ExecutionContext, type: str) -> AbstractResponse:
    from wexample_wex_core.response.dict_response import DictResponse
    from wexample_wex_core.response.list_response import ListResponse

    if type == PING_TYPE_LIST:
        return ListResponse(kernel=context.kernel, content=["pong", "ping", "pang"])

    return DictResponse(kernel=context.kernel, content={"status": "pong"})
