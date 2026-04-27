from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_app.common.command_request import CommandRequest as BaseCommandRequest
from wexample_helpers.classes.field import public_field
from wexample_helpers.decorator.base_class import base_class

if TYPE_CHECKING:
    pass


@base_class
class CommandRequest(BaseCommandRequest):
    request_id: str = public_field(
        factory=lambda: __import__("uuid").uuid4().hex,
        description="Unique identifier for this request (auto-generated if not provided)",
    )

    def __attrs_post_init__(self) -> None:
        from wexample_app.exception.app_runtime_exception import AppRuntimeException
        from wexample_app.exception.command_type_not_found_exception import (
            CommandTypeNotFoundException,
        )

        try:
            super().__attrs_post_init__()
        except CommandTypeNotFoundException:
            if "_" in self.name:
                suggested = self.name.replace("_", "-")
                raise AppRuntimeException(
                    f"Command names use hyphens not underscores. Did you mean: '{suggested}'?"
                )
            raise

    def get_addon_manager(self):
        return self.resolver.get_request_addon_manager(self)
