from typing import Optional

from wexample_app.exception.abstract_exception import AbstractException, ExceptionData


class AddonNotRegisteredData(ExceptionData):
    """Data model for AddonNotRegistered exception."""
    addon_name: str


class AddonNotRegisteredException(AbstractException):
    """Exception raised when trying to access an addon that is not registered."""
    error_code: str = "ADDON_NOT_REGISTERED"

    def __init__(
            self,
            addon_name: str,
            cause: Optional[Exception] = None,
            previous: Optional[Exception] = None
    ):
        # Create structured data using Pydantic model
        data_model = AddonNotRegisteredData(addon_name=addon_name)

        # Store addon_name as instance attribute
        self.addon_name = addon_name

        super().__init__(
            message=f"Addon '{addon_name}' is not registered",
            data=data_model.model_dump(),
            cause=cause,
            previous=previous
        )
