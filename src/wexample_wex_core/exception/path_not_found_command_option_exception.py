from __future__ import annotations

from typing import ClassVar

from attrs import Factory
from wexample_helpers.classes.field import public_field
from wexample_helpers.decorator.base_class import base_class

from wexample_cli.exception.abstract_command_option_exception import (
    AbstractCommandOptionException,
)


@base_class
class PathNotFoundCommandOptionException(AbstractCommandOptionException):
    """Exception raised when a file specified in a command option is not found."""

    error_code: ClassVar[str] = "FILE_NOT_FOUND_COMMAND_OPTION"

    file_path: str = public_field(description="Path that was not found")
    message: str = public_field(
        default=Factory(
            lambda self: f"File or directory not found, specified in option '{self.option_name}': '{self.file_path}'",
            takes_self=True,
        ),
        description="Human-readable error message",
    )
