from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

from wexample_helpers.helpers.file import (
    file_get_dir_size,
    file_get_human_readable_size,
)

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON
from wexample_wex_core.decorator.command import command
from wexample_wex_core.decorator.option import option

if TYPE_CHECKING:
    from wexample_wex_core.context.execution_context import ExecutionContext


@option(
    "path",
    type=str,
    short_name="p",
    required=False,
    default=None,
    description="Directory to inspect (default: cwd)",
)
@command(
    type=COMMAND_TYPE_ADDON,
    description="Return size of entries in a directory, sorted ascending",
)
def system__dir__spaces(
    context: ExecutionContext, path: str | None = None
) -> TableResponse:
    from wexample_app.response.table_response import TableResponse

    base = Path(path) if path else Path(os.getcwd())
    entries = sorted(
        base.iterdir(),
        key=lambda e: (
            file_get_dir_size(e)
            if e.is_dir()
            else (e.stat().st_size if e.is_file() and not e.is_symlink() else 0)
        ),
    )

    rows = []
    for entry in entries:
        if entry.is_dir():
            size = file_get_dir_size(entry)
        elif entry.is_file() and not entry.is_symlink():
            try:
                size = entry.stat().st_size
            except OSError:
                continue
        else:
            continue
        rows.append([file_get_human_readable_size(size), entry.name])

    return TableResponse(kernel=context.kernel, headers=["Size", "Name"], content=rows)
