from __future__ import annotations

from pathlib import Path

from wexample_app.output.app_file_output_handler import AppFileOutputHandler
from wexample_helpers.classes.field import public_field
from wexample_helpers.decorator.base_class import base_class

from wexample_wex_core.common.command_request import CommandRequest


@base_class
class RequestFileOutputHandler(AppFileOutputHandler):
    """Extended file output handler for core kernel with predefined output path."""

    file_path: Path = public_field(default=None, description="Path to the output file")

    def _get_file_path(self, request: CommandRequest) -> Path:
        from wexample_app.const.globals import APP_PATH_APP_MANAGER
        from wexample_app.const.path import APP_DIR_PATH_RELATIVE_OUTPUT

        return (
            request.kernel._call_workdir.get_path()
            / APP_PATH_APP_MANAGER
            / APP_DIR_PATH_RELATIVE_OUTPUT
            / request.request_id
        )
