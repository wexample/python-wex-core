from __future__ import annotations

from typing import ClassVar

from wexample_helpers.classes.field import public_field
from wexample_helpers.decorator.base_class import base_class
from wexample_helpers.exception.not_allowed_item_exception import (
    NotAllowedItemException,
)


@base_class
class AddonNotRegisteredException(NotAllowedItemException):
    """Exception raised when trying to access an addon that is not registered.

    This exception extends NotAllowedItemException to provide a standardized way
    of handling cases where an addon name is not in the list of registered addons.
    """

    addon_name: str = public_field(description="Name of the unregistered addon")
    available_addons: list[str] = public_field(
        factory=list,
        description="List of registered addon names",
    )
    error_code: ClassVar[str] = "ADDON_NOT_REGISTERED"
    item_type: str = public_field(
        default="addon",
        description="Type of the offending item",
    )

    def _build_message(self) -> str:
        return self.format_not_allowed_item_message(
            item_type="addon",
            item_value=self.addon_name,
            allowed_values=self.available_addons,
        )
