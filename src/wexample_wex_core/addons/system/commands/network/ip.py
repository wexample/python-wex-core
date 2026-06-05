from __future__ import annotations

import socket
from typing import TYPE_CHECKING

from wexample_cli.decorator.command import command
from wexample_cli.const.tags import AudienceTag, EffectTag, ScopeTag
from wexample_wex_core.addons.system.const.tags import DomainTag

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON

if TYPE_CHECKING:
    from wexample_cli.context.execution_context import ExecutionContext


@command(
    type=COMMAND_TYPE_ADDON, description="Return the current system local IP address",
    tags=[
        DomainTag.SYSTEM,
        EffectTag.READ_ONLY,
        AudienceTag.AGENT_SAFE,
        ScopeTag.HOST,
        ScopeTag.LOCAL,
    ],
)
def system__network__ip(context: ExecutionContext) -> str:
    host_name = socket.gethostname()
    return socket.gethostbyname(host_name)
