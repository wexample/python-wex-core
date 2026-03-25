from __future__ import annotations

from wexample_helpers.classes.field import public_field
from wexample_helpers.decorator.base_class import base_class

from wexample_app.response.abstract_response import AbstractResponse


@base_class
class QueuedCollectionStopCurrentStepResponse(AbstractResponse):
    """Stop the current step only — queue continues with the next step."""

    reason: str = public_field(description="Why this step was skipped")

    def get_printable(self) -> str | None:
        return None
