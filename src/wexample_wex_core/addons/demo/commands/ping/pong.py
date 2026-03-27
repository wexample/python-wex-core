from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON
from wexample_wex_core.decorator.alias import alias
from wexample_wex_core.decorator.command import command
from wexample_wex_core.decorator.option import option

if TYPE_CHECKING:
    from wexample_app.response.abstract_response import AbstractResponse
    from wexample_wex_core.context.execution_context import ExecutionContext

PING_TYPE_DICT = "dict"
PING_TYPE_LIST = "list"
PING_TYPE_TABLE = "table"
PING_TYPE_COLLECTION = "collection"
PING_TYPE_QUEUED = "queued"


@alias("ping")
@option(name="type", type=str, required=True, description="Response type to return (dict, list, table, collection, queued)")
@command(type=COMMAND_TYPE_ADDON)
def demo__ping__pong(context: ExecutionContext, type: str) -> AbstractResponse:
    from wexample_wex_core.response.dict_response import DictResponse
    from wexample_wex_core.response.list_response import ListResponse
    from wexample_wex_core.response.response_collection_response import ResponseCollectionResponse
    from wexample_wex_core.response.table_response import TableResponse

    if type == PING_TYPE_LIST:
        return ListResponse(kernel=context.kernel, content=["pong", "ping", "pang"])

    if type == PING_TYPE_TABLE:
        return TableResponse(
            kernel=context.kernel,
            headers=["name", "status"],
            content=[["ping", "ok"], ["pong", "ok"]],
        )

    if type == PING_TYPE_COLLECTION:
        return ResponseCollectionResponse(
            kernel=context.kernel,
            content=[
                DictResponse(kernel=context.kernel, content={"status": "pong"}),
                ListResponse(kernel=context.kernel, content=["pong", "ping", "pang"]),
            ],
        )

    if type == PING_TYPE_QUEUED:
        from wexample_wex_core.response.queued_collection_response import QueuedCollectionResponse

        return QueuedCollectionResponse(
            kernel=context.kernel,
            content=[
                DictResponse(kernel=context.kernel, content={"step": "one"}),
                lambda previous_value: ListResponse(
                    kernel=context.kernel,
                    content=["step-two", str(previous_value)],
                ),
            ],
        )

    return DictResponse(kernel=context.kernel, content={"status": "pong"})
