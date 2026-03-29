from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON
from wexample_wex_core.decorator.as_sudo import as_sudo
from wexample_wex_core.decorator.command import command

if TYPE_CHECKING:
    from wexample_app.response.abstract_response import AbstractResponse
    from wexample_wex_core.context.execution_context import ExecutionContext


@as_sudo()
@command(type=COMMAND_TYPE_ADDON, description="Demo command that requires sudo")
def demo__sudo__check(context: ExecutionContext) -> AbstractResponse:
    import os

    from wexample_app.response.dict_response import DictResponse

    return DictResponse(
        kernel=context.kernel,
        content={"user": os.getenv("USER", "unknown"), "uid": os.getuid()},
    )
