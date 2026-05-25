from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_cli.decorator.alias import alias
from wexample_cli.decorator.command import command
from wexample_cli.decorator.option import option

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON

if TYPE_CHECKING:
    from wexample_app.response.abstract_response import AbstractResponse
    from wexample_cli.context.execution_context import ExecutionContext

PING_TYPE_BOOL = "bool"
PING_TYPE_COLLECTION = "collection"
PING_TYPE_DICT = "dict"
PING_TYPE_FUNCTION = "function"
PING_TYPE_INT = "int"
PING_TYPE_LIST = "list"
PING_TYPE_NULL = "null"
PING_TYPE_QUEUED = "queued"
PING_TYPE_SHELL = "shell"
PING_TYPE_STR = "str"
PING_TYPE_TABLE = "table"


@alias("ping")
@option(
    name="type",
    type=str,
    required=True,
    description="Response type to return (bool, dict, function, int, list, null, queued, shell, str, table, collection)",
)
@command(type=COMMAND_TYPE_ADDON)
def demo__ping__pong(context: ExecutionContext, type: str) -> AbstractResponse:
    from wexample_app.response.dict_response import DictResponse
    from wexample_app.response.list_response import ListResponse
    from wexample_app.response.response_collection_response import (
        ResponseCollectionResponse,
    )
    from wexample_app.response.table_response import TableResponse

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

    if type == PING_TYPE_FUNCTION:
        from wexample_app.response.dict_response import DictResponse
        from wexample_app.response.function_response import FunctionResponse

        return FunctionResponse(
            kernel=context.kernel,
            content=lambda: DictResponse(
                kernel=context.kernel, content={"status": "pong"}
            ),
        )

    if type == PING_TYPE_SHELL:
        from wexample_app.response.shell_command_response import ShellCommandResponse

        return ShellCommandResponse(kernel=context.kernel, content=["echo", "pong"])

    if type == PING_TYPE_QUEUED:
        from wexample_app.response.queued_collection_response import (
            QueuedCollectionResponse,
        )

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

    if type == PING_TYPE_STR:
        from wexample_app.response.str_response import StrResponse

        return StrResponse(kernel=context.kernel, content="pong")

    if type == PING_TYPE_INT:
        from wexample_app.response.int_response import IntResponse

        return IntResponse(kernel=context.kernel, content=42)

    if type == PING_TYPE_BOOL:
        from wexample_app.response.boolean_response import BooleanResponse

        return BooleanResponse(kernel=context.kernel, content=True)

    if type == PING_TYPE_NULL:
        from wexample_app.response.null_response import NullResponse

        return NullResponse(kernel=context.kernel)

    return DictResponse(kernel=context.kernel, content={"status": "pong"})
