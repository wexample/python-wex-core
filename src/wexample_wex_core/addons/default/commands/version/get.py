from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON
from wexample_wex_core.decorator.alias import alias
from wexample_wex_core.decorator.command import command

if TYPE_CHECKING:
    from wexample_wex_core.context.execution_context import ExecutionContext


@alias("version")
@command(
    type=COMMAND_TYPE_ADDON,
    description="Returns core version",
)
def default__version__get(context: ExecutionContext) -> str:
    from pathlib import Path

    version_file = Path(context.kernel.entrypoint_path).parent / "version.txt"
    return version_file.read_text().strip()
