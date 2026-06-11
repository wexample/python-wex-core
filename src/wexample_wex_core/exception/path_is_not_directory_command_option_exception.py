from __future__ import annotations

from typing import ClassVar

from wexample_cli.exception.abstract_command_option_exception import (
    AbstractCommandOptionException,
)
from wexample_helpers.classes.field import public_field
from wexample_helpers.decorator.base_class import base_class


@base_class
class PathIsNotDirectoryCommandOptionException(AbstractCommandOptionException):
    """Exception raised when a path specified in a command option exists but is not a directory."""

    directory_path: str = public_field(description="Path that is not a directory")
    error_code: ClassVar[str] = "PATH_IS_NOT_DIRECTORY_COMMAND_OPTION"

    def _build_message(self) -> str:
        return f"Path exists but is not a directory, specified in option '{self.option_name}': '{self.directory_path}'"
