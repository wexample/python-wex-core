from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_cli.decorator.command import command
from wexample_cli.decorator.option import option
from wexample_helpers.const.types import UPGRADE_TYPE_MINOR

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON

if TYPE_CHECKING:
    from wexample_cli.context.execution_context import ExecutionContext


@option(name="version", type=str, required=True)
@option(name="type", type=str)
@option(name="increment", type=int)
@option(name="build", type=bool)
@command(type=COMMAND_TYPE_ADDON)
def core__version__increment(
    context: ExecutionContext,
    version: str,
    type: str = UPGRADE_TYPE_MINOR,
    increment: int = 1,
    build: bool = False,
) -> str:
    from wexample_helpers.helpers.version import version_increment

    return version_increment(
        version=version,
        type=type,
        increment=increment,
        build=build,
    )
