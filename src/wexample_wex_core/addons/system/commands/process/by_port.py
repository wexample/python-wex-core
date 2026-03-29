from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import psutil

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON
from wexample_wex_core.decorator.command import command
from wexample_wex_core.decorator.option import option

if TYPE_CHECKING:
    from wexample_wex_core.context.execution_context import ExecutionContext

_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


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
@command(type=COMMAND_TYPE_ADDON, description="Return info about the process listening on a port")
def system__process__by_port(context: "ExecutionContext", port: int):
    from wexample_app.response.dict_response import DictResponse

    proc = _find_process_by_port(port)

    if proc:
        try:
            data = {
                "name": proc.name(),
                "port": port,
                "pid": proc.pid,
                "status": proc.status(),
                "started": datetime.fromtimestamp(proc.create_time()).strftime(_DATE_FORMAT),
                "command": proc.cmdline(),
                "running": True,
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            data = {"port": port, "running": False}
    else:
        data = {"port": port, "running": False}

    return DictResponse(kernel=context.kernel, content=data)
