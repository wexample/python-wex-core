from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON
from wexample_cli.decorator.alias import alias
from wexample_cli.decorator.as_sudo import as_sudo
from wexample_cli.decorator.command import command

if TYPE_CHECKING:
    from wexample_app.response.abstract_response import AbstractResponse

    from wexample_cli.context.execution_context import ExecutionContext


@alias("upgrade")
@as_sudo()
@command(
    type=COMMAND_TYPE_ADDON,
    description="Upgrade wex to the latest version via apt",
)
def core__self__upgrade(context: ExecutionContext) -> AbstractResponse:
    from wexample_app.response.interactive_shell_command_response import (
        InteractiveShellCommandResponse,
    )

    return InteractiveShellCommandResponse(
        kernel=context.kernel,
        content=["bash", "-c", "apt-get update -q && apt-get install -y wex"],
    )
