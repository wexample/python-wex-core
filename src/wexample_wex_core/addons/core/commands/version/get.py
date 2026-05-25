from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON
from wexample_cli.decorator.alias import alias
from wexample_cli.decorator.command import command

if TYPE_CHECKING:
    from wexample_cli.context.execution_context import ExecutionContext


@alias("version")
@command(
    type=COMMAND_TYPE_ADDON,
    description="Returns core version",
)
def core__version__get(context: ExecutionContext) -> str:
    return context.kernel.workdir.get_setup_version()
