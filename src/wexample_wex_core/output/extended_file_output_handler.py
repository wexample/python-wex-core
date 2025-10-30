from __future__ import annotations

from pathlib import Path

from wexample_app.output.app_file_output_handler import AppFileOutputHandler
from wexample_helpers.classes.field import public_field
from wexample_helpers.decorator.base_class import base_class


@base_class
class ExtendedFileOutputHandler(AppFileOutputHandler):
    """Extended file output handler for core kernel with predefined output path."""

    file_path: Path = public_field(
        default=None,
        description="Path to the output file"
    )

    def __attrs_post_init__(self) -> None:
        """Set the default file path to output.txt."""

        if not self.file_path:
            self.file_path = Path("output.txt")

