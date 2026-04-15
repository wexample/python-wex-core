from __future__ import annotations

import json
from datetime import datetime
from typing import TYPE_CHECKING

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON
from wexample_wex_core.decorator.command import command
from wexample_wex_core.decorator.option import option
from wexample_wex_core.webhook.const import WEBHOOK_LISTEN_PORT_DEFAULT

if TYPE_CHECKING:
    from wexample_app.response.abstract_response import AbstractResponse
    from wexample_wex_core.context.execution_context import ExecutionContext

_DATE_FMT = "%Y-%m-%d %H:%M:%S"
_LOG_TAIL = 20  # last N entries shown by default


@option("port", type=int, short_name="p", required=False, default=WEBHOOK_LISTEN_PORT_DEFAULT, description="Port the daemon should be listening on")
@option("lines", type=int, short_name="n", required=False, default=_LOG_TAIL, description="Number of recent log entries to display")
@command(type=COMMAND_TYPE_ADDON, description="Show webhook daemon status and recent log entries")
def default__webhook__status(
    context: ExecutionContext,
    port: int = WEBHOOK_LISTEN_PORT_DEFAULT,
    lines: int = _LOG_TAIL,
) -> AbstractResponse | None:
    from wexample_app.response.dict_response import DictResponse
    from wexample_wex_core.addons.system.helpers import system_find_process_by_port

    proc = system_find_process_by_port(port)

    # ---- process info -------------------------------------------------------
    if proc:
        try:
            started = datetime.fromtimestamp(proc.create_time()).strftime(_DATE_FMT)
            process_info: dict = {
                "running": True,
                "pid": proc.pid,
                "port": port,
                "started": started,
                "status": proc.status(),
            }
        except Exception:
            process_info = {"running": False, "port": port}
    else:
        process_info = {"running": False, "port": port}

    # ---- recent log entries -------------------------------------------------
    log_path = _resolve_log_path(context)
    recent: list[dict] = _tail_log(log_path, lines)

    result = {
        "daemon": process_info,
        "log_path": log_path,
        "recent_requests": recent,
    }

    if not process_info["running"]:
        context.io.warning(f"No webhook daemon found on port {port}")

    return DictResponse(kernel=context.kernel, content=result)


def _resolve_log_path(context: ExecutionContext) -> str:
    from pathlib import Path

    log_dir = Path(context.kernel.workdir.get_path()) / "logs"
    return str(log_dir / "webhook.log")


def _tail_log(log_path: str, n: int) -> list[dict]:
    """Return the last *n* JSON-line entries from the log file."""
    from pathlib import Path

    path = Path(log_path)
    if not path.exists():
        return []

    entries: list[dict] = []
    try:
        with open(path) as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    except OSError:
        return []

    return entries[-n:]
