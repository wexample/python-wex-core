from __future__ import annotations

from typing import ClassVar

from wexample_cli.exception.abstract_command_option_exception import (
    AbstractCommandOptionException,
)
from wexample_helpers.classes.field import public_field
from wexample_helpers.decorator.base_class import base_class


@base_class
class PathIsNotFileCommandOptionException(AbstractCommandOptionException):
    """Exception raised when a path specified in a command option exists but is not a file."""

    error_code: ClassVar[str] = "PATH_IS_NOT_FILE_COMMAND_OPTION"
    file_path: str = public_field(description="Path that is not a file")

    def _build_message(self) -> str:
        return f"Path exists but is not a file, specified in option '{self.option_name}': '{self.file_path}'"
