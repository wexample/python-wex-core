from __future__ import annotations

import platform
from typing import TYPE_CHECKING

from wexample_cli.const.tags import AudienceTag, EffectTag, ScopeTag
from wexample_cli.decorator.command import command

from wexample_wex_core.addons.system.const.tags import DomainTag
from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON

if TYPE_CHECKING:
    from wexample_cli.context.execution_context import ExecutionContext

OS_NAME_LINUX: str = "linux"
OS_NAME_MAC: str = "mac"
OS_NAME_WINDOWS: str = "windows"
OS_NAME_UNDEFINED: str = "undefined"


@command(
    type=COMMAND_TYPE_ADDON,
    description="Return the local OS name",
    tags=[
        DomainTag.SYSTEM,
        EffectTag.READ_ONLY,
        AudienceTag.AGENT_SAFE,
        ScopeTag.HOST,
        ScopeTag.LOCAL,
    ],
)
def system__os__name(context: ExecutionContext) -> str:
    os_name = platform.system()

    if os_name == "Darwin":
        return OS_NAME_MAC
    elif os_name == "Linux":
        return OS_NAME_LINUX
    elif os_name in ("CYGWIN", "MINGW32", "MINGW64", "MSYS"):
        return OS_NAME_WINDOWS
    else:
        return OS_NAME_UNDEFINED
