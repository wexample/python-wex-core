from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON
from wexample_wex_core.decorator.attach import ATTACH_POSITION_AFTER, attach
from wexample_wex_core.decorator.command import command

if TYPE_CHECKING:
    from wexample_app.response.abstract_response import AbstractResponse
    from wexample_wex_core.context.execution_context import ExecutionContext

_HOOK_CALLED: list[str] = []


@attach(position=ATTACH_POSITION_AFTER, command="demo::ping/pong")
@command(type=COMMAND_TYPE_ADDON, description="Demo after-hook for demo::ping/pong")
def demo__hook__after_ping(context: ExecutionContext) -> AbstractResponse:
    from wexample_app.response.default_response import DefaultResponse

    _HOOK_CALLED.append("after_ping")
    return DefaultResponse(kernel=context.kernel, content="hook ran")
