from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON
from wexample_cli.decorator.alias import alias
from wexample_cli.decorator.command import command

if TYPE_CHECKING:
    from wexample_app.response.abstract_response import AbstractResponse

    from wexample_cli.context.execution_context import ExecutionContext


@alias("hi")
@command(
    type=COMMAND_TYPE_ADDON,
    description="Return hi! Used to check if core vitals are working",
)
def core__ping__hi(context: ExecutionContext) -> AbstractResponse:
    from wexample_app.response.default_response import DefaultResponse

    return DefaultResponse(kernel=context.kernel, content="hi!")
