from typing import Optional

from pydantic import ValidationError

from wexample_app.exception.abstract_exception import AbstractException, ExceptionData


class CommandOptionMissingArgumentData(ExceptionData):
    """Data model for CommandOptionMissingArgument exception."""
    argument_name: str
    decorator_name: str


class CommandOptionMissingArgumentException(AbstractException):
    """Exception raised when a required argument is missing in a command option decorator."""
    error_code: str = "COMMAND_OPTION_MISSING_ARGUMENT"

    def __init__(
            self,
            cause: Optional[Exception] = None,
            previous: Optional[Exception] = None
    ):
        assert isinstance(previous, ValidationError)

        super().__init__(
            message='Missing argument definition in @option declaration',
            cause=cause,
            previous=previous
        )
