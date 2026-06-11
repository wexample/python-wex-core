from __future__ import annotations

from typing import ClassVar

from attrs import Factory
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

    error_code: ClassVar[str] = "ADDON_NOT_REGISTERED"

    addon_name: str = public_field(description="Name of the unregistered addon")
    available_addons: list[str] | None = public_field(
        default=None,
        description="List of registered addon names",
    )
    item_type: str = public_field(
        default="addon",
        description="Type of the offending item",
    )
    item_value: str | None = public_field(
        default=Factory(lambda self: self.addon_name, takes_self=True),
        description="Value of the item that is not allowed",
    )
    allowed_values: list[str] = public_field(
        default=Factory(lambda self: self.available_addons or [], takes_self=True),
        description="List of allowed values for this item type",
    )
    message: str = public_field(
        default=Factory(
            lambda self: self.format_not_allowed_item_message(
                item_type=self.item_type,
                item_value=self.item_value,
                allowed_values=self.allowed_values,
            ),
            takes_self=True,
        ),
        description="Human-readable error message",
    )
