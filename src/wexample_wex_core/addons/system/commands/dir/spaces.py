from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON
from wexample_wex_core.decorator.command import command
from wexample_wex_core.decorator.option import option

if TYPE_CHECKING:
    from wexample_wex_core.context.execution_context import ExecutionContext


def _dir_size(path: Path) -> int:
    total = 0
    try:
        for entry in path.rglob("*"):
            try:
                if entry.is_file() and not entry.is_symlink():
                    total += entry.stat().st_size
            except OSError:
                pass
    except OSError:
        pass
    return total


def _human_readable(size: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"


@option("path", type=str, short_name="p", required=False, default=None, description="Directory to inspect (default: cwd)")
@command(type=COMMAND_TYPE_ADDON, description="Return size of entries in a directory, sorted ascending")
def system__dir__spaces(context: "ExecutionContext", path: Optional[str] = None):
    from wexample_app.response.table_response import TableResponse

    base = Path(path) if path else Path(os.getcwd())
    entries = sorted(base.iterdir(), key=lambda e: (
        _dir_size(e) if e.is_dir() else (e.stat().st_size if e.is_file() and not e.is_symlink() else 0)
    ))

    rows = []
    for entry in entries:
        if entry.is_dir():
            size = _dir_size(entry)
        elif entry.is_file() and not entry.is_symlink():
            try:
                size = entry.stat().st_size
            except OSError:
                continue
        else:
            continue
        rows.append([_human_readable(size), entry.name])

    return TableResponse(kernel=context.kernel, headers=["Size", "Name"], content=rows)
