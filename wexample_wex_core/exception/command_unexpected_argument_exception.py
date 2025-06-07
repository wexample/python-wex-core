from typing import Optional

from wexample_app.exception.abstract_exception import AbstractException, ExceptionData


class CommandUnexpectedArgumentData(ExceptionData):
    """Data model for CommandUnexpectedArgument exception."""
    argument: str


class CommandUnexpectedArgumentException(AbstractException):
    """Exception raised when an unexpected argument is provided to a command."""
    error_code: str = "COMMAND_UNEXPECTED_ARGUMENT"

    def __init__(
            self,
            argument: str,
            cause: Optional[Exception] = None,
            previous: Optional[Exception] = None
    ):
        # Create structured data using Pydantic model
        data_model = CommandUnexpectedArgumentData(argument=argument)

        # Store argument as instance attribute
        self.argument = argument

        super().__init__(
            message=f"Unexpected argument: {argument}",
            data=data_model.model_dump(),
            cause=cause,
            previous=previous
        )
