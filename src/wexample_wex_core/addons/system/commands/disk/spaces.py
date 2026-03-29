from __future__ import annotations

from typing import TYPE_CHECKING

import psutil

from wexample_helpers.helpers.file import file_get_human_readable_size
from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON
from wexample_wex_core.decorator.command import command

if TYPE_CHECKING:
    from wexample_wex_core.context.execution_context import ExecutionContext


@command(type=COMMAND_TYPE_ADDON, description="Return space usage of current system disks")
def system__disk__spaces(context: "ExecutionContext"):
    from wexample_app.response.table_response import TableResponse

    rows = []
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError:
            continue
        rows.append([
            file_get_human_readable_size(usage.total),
            file_get_human_readable_size(usage.used),
            file_get_human_readable_size(usage.free),
            f"{usage.percent}%",
            partition.mountpoint,
            partition.device,
        ])

    return TableResponse(
        kernel=context.kernel,
        headers=["Size", "Used", "Avail", "Usage", "Mounted", "Filesystem"],
        content=rows,
    )
