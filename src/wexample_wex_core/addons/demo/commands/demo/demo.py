from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_cli.decorator.command import command

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON

if TYPE_CHECKING:
    from wexample_app.response.abstract_response import AbstractResponse
    from wexample_cli.context.execution_context import ExecutionContext


@command(type=COMMAND_TYPE_ADDON)
def demo__demo__demo(context: ExecutionContext) -> AbstractResponse:
    from wexample_app.response.str_response import StrResponse

    return StrResponse(kernel=context.kernel, content="demo")
