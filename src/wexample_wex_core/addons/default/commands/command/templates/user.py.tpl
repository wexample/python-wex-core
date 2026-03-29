from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_wex_core.const.globals import COMMAND_TYPE_USER
from wexample_wex_core.decorator.command import command

if TYPE_CHECKING:
    from wexample_wex_core.context.execution_context import ExecutionContext


@command(type=COMMAND_TYPE_USER, description="")
def user__{group}__{name}(context: "ExecutionContext") -> None:
    context.io.log("Hello from ~{group}/{name}")
