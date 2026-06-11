from __future__ import annotations

from typing import ClassVar

from attrs import Factory
from wexample_helpers.classes.field import public_field
from wexample_helpers.decorator.base_class import base_class

from wexample_cli.exception.abstract_command_option_exception import (
    AbstractCommandOptionException,
)


@base_class
class PathIsNotDirectoryCommandOptionException(AbstractCommandOptionException):
    """Exception raised when a path specified in a command option exists but is not a directory."""

    error_code: ClassVar[str] = "PATH_IS_NOT_DIRECTORY_COMMAND_OPTION"

    directory_path: str = public_field(description="Path that is not a directory")
    message: str = public_field(
        default=Factory(
            lambda self: f"Path exists but is not a directory, specified in option '{self.option_name}': '{self.directory_path}'",
            takes_self=True,
        ),
        description="Human-readable error message",
    )
