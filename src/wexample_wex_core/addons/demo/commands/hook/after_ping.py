from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_wex_core.addons.demo.commands.ping.pong import demo__ping__pong
from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON
from wexample_wex_core.decorator.attach import ATTACH_POSITION_AFTER, attach
from wexample_wex_core.decorator.command import command

if TYPE_CHECKING:
    from wexample_app.response.abstract_response import AbstractResponse
    from wexample_wex_core.context.execution_context import ExecutionContext


@attach(position=ATTACH_POSITION_AFTER, command=demo__ping__pong)
@command(type=COMMAND_TYPE_ADDON, description="Demo after-hook for demo::ping/pong")
def demo__hook__after_ping(context: ExecutionContext) -> AbstractResponse:
    from wexample_app.response.default_response import DefaultResponse

    context.kernel.io.log("@attach after demo::ping/pong — hook ran!")
    # Store on kernel so the test can observe the side-effect across module boundaries.
    context.kernel._test_after_ping_ran = True
    return DefaultResponse(kernel=context.kernel, content="hook ran")
