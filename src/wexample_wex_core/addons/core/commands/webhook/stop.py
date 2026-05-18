from __future__ import annotations

from typing import TYPE_CHECKING

import psutil

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON
from wexample_wex_core.decorator.command import command
from wexample_wex_core.decorator.option import option
from wexample_wex_core.webhook.const import WEBHOOK_LISTEN_PORT_DEFAULT

if TYPE_CHECKING:
    from wexample_wex_core.context.execution_context import ExecutionContext


@option(
    "port",
    type=int,
    short_name="p",
    required=False,
    default=WEBHOOK_LISTEN_PORT_DEFAULT,
    description="Port the daemon is listening on",
)
@command(type=COMMAND_TYPE_ADDON, description="Stop the webhook daemon")
def core__webhook__stop(
    context: ExecutionContext,
    port: int = WEBHOOK_LISTEN_PORT_DEFAULT,
) -> None:
    from wexample_wex_core.addons.system.helpers import system_find_process_by_port
    from wexample_wex_core.webhook.daemon_marker import marker_clear

    proc = system_find_process_by_port(port)

    if not proc:
        context.io.log(f"No webhook daemon found on port {port}")
        marker_clear(context.kernel.workdir.get_path())
        return

    pid = proc.pid
    context.io.log(f"Stopping webhook daemon on port {port} (pid {pid})...")

    try:
        proc.terminate()
        proc.wait(timeout=5)
        context.io.log(f"Daemon stopped (pid {pid})")
    except psutil.TimeoutExpired:
        proc.kill()
        context.io.log(f"Daemon force-killed (pid {pid})")
    except psutil.NoSuchProcess:
        context.io.log(f"Process {pid} already gone")

    marker_clear(context.kernel.workdir.get_path())
