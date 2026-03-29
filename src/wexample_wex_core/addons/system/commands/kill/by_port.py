from __future__ import annotations

from typing import TYPE_CHECKING

import psutil

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON
from wexample_wex_core.decorator.as_sudo import as_sudo
from wexample_wex_core.decorator.command import command
from wexample_wex_core.decorator.option import option

if TYPE_CHECKING:
    from wexample_wex_core.context.execution_context import ExecutionContext


def _find_process_by_port(port: int) -> psutil.Process | None:
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            for conn in proc.net_connections():
                if conn.laddr.port == port:
                    return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return None


@option("port", type=int, short_name="p", required=True, description="Port number")
@as_sudo()
@command(type=COMMAND_TYPE_ADDON, description="Kill the process listening on a port")
def system__kill__by_port(context: "ExecutionContext", port: int) -> None:
    proc = _find_process_by_port(port)

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
