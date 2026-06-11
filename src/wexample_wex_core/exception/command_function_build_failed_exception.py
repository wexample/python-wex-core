from __future__ import annotations

from typing import ClassVar

from wexample_helpers.classes.field import public_field
from wexample_helpers.decorator.base_class import base_class
from wexample_helpers.exception.undefined_exception import UndefinedException


@base_class
class CommandFunctionBuildFailedException(UndefinedException):
    """Exception raised when a command function could not be built correctly.

    This exception is thrown when the system tries to build a command function but
    the result is not of the expected type, indicating an issue with the command
    declaration or implementation.
    """

    error_code: ClassVar[str] = "COMMAND_FUNCTION_BUILD_FAILED"

    command_name: str = public_field(description="Name of the command being built")
    expected_type: str = public_field(description="Expected command function type")
    actual_type: str = public_field(description="Actual type that was produced")

    def _build_message(self) -> str:
        return f"Failed to build command function for '{self.command_name}'. Expected type '{self.expected_type}' but got '{self.actual_type}'."
