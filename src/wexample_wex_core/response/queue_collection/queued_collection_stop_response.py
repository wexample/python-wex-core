from __future__ import annotations

from wexample_helpers.classes.field import public_field
from wexample_helpers.decorator.base_class import base_class

from wexample_app.response.abstract_response import AbstractResponse


@base_class
class QueuedCollectionStopResponse(AbstractResponse):
    """Stop the entire queue execution."""

    reason: str = public_field(description="Why the queue was stopped")

    def get_printable(self) -> str | None:
        return None
