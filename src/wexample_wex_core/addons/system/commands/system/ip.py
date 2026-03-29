from __future__ import annotations

import socket
from typing import TYPE_CHECKING

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON
from wexample_wex_core.decorator.command import command

if TYPE_CHECKING:
    from wexample_wex_core.context.execution_context import ExecutionContext


@command(type=COMMAND_TYPE_ADDON, description="Return the current system local IP address")
def system__system__ip(context: "ExecutionContext") -> str:
    host_name = socket.gethostname()
    return socket.gethostbyname(host_name)
