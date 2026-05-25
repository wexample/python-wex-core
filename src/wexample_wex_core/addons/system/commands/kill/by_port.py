from __future__ import annotations

from typing import TYPE_CHECKING

import psutil

from wexample_wex_core.addons.system.helpers import system_find_process_by_port
from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON
from wexample_cli.decorator.as_sudo import as_sudo
from wexample_cli.decorator.command import command
from wexample_cli.decorator.option import option

if TYPE_CHECKING:
    from wexample_cli.context.execution_context import ExecutionContext


@option("port", type=int, short_name="p", required=True, description="Port number")
@as_sudo()
@command(type=COMMAND_TYPE_ADDON, description="Kill the process listening on a port")
def system__kill__by_port(context: ExecutionContext, port: int) -> None:
    proc = system_find_process_by_port(port)

    if proc:
        try:
            proc.terminate()
            proc.wait(timeout=5)
            context.io.success(f"Process {proc.pid} on port {port} terminated")
        except psutil.TimeoutExpired:
            proc.kill()
            context.io.success(f"Process {proc.pid} on port {port} killed (force)")
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            context.io.error(f"Could not kill process on port {port}: {e}")
    else:
        context.io.warning(f"No process found on port {port}")
