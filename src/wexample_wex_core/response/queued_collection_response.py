from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Callable

from wexample_helpers.classes.field import public_field
from wexample_helpers.decorator.base_class import base_class

from wexample_app.response.abstract_response import AbstractResponse

if TYPE_CHECKING:
    from wexample_app.const.types import ResponsePrintable

QueueStep = AbstractResponse | Callable | Any

_SENTINEL = object()


@base_class
class QueuedCollectionResponse(AbstractResponse):
    """Execute a list of steps sequentially.

    Each step can be:
    - An AbstractResponse (rendered as-is)
    - A callable (called with previous_value if its signature accepts it)
    - A plain value (str, int, dict, list…) wrapped via response_normalize
    - A nested QueuedCollectionResponse (executed inline, last value propagated)

    QueuedCollectionStopResponse halts the entire queue.
    QueuedCollectionStopCurrentStepResponse skips the step and continues.
    """

    content: list[QueueStep] = public_field(
        default_factory=list,
        description="Ordered list of steps to execute sequentially",
    )

    def __attrs_post_init__(self) -> None:
        self._execute_super_attrs_post_init_if_exists()
        self._last_value: Any = _SENTINEL

    def _resolve_step(self, step: QueueStep, previous_value: Any) -> AbstractResponse:
        from wexample_helpers.helpers.args import args_in_function
        from wexample_app.helpers.response import response_normalize

        if callable(step):
            kwargs = {}
            if args_in_function(step, "previous_value"):
                kwargs["previous_value"] = previous_value
            result = step(**kwargs)
            return response_normalize(kernel=self.kernel, response=result)

        if isinstance(step, AbstractResponse):
            return step

        return response_normalize(kernel=self.kernel, response=step)

    def _extract_value(self, response: AbstractResponse) -> Any:
        """Extract the meaningful value from an already-executed response."""
        if isinstance(response, QueuedCollectionResponse):
            # Already executed — read stored last value, don't re-run
            last = response._last_value
            return last if last is not _SENTINEL else None

        return response.content

    def get_formatted(self, output_format: str) -> str:
        from wexample_app.const.output import OUTPUT_FORMAT_STR
        from wexample_wex_core.response.queue_collection.queued_collection_stop_current_step_response import (
            QueuedCollectionStopCurrentStepResponse,
        )
        from wexample_wex_core.response.queue_collection.queued_collection_stop_response import (
            QueuedCollectionStopResponse,
        )

        previous_value: Any = None
        json_results: list = []

        for step in self.content:
            response = self._resolve_step(step, previous_value)

            if isinstance(response, QueuedCollectionStopResponse):
                break

            if isinstance(response, QueuedCollectionStopCurrentStepResponse):
                continue

            output = response.get_formatted(output_format)
            previous_value = self._extract_value(response)

            if output_format != OUTPUT_FORMAT_STR and output:
                import json
                try:
                    json_results.append(json.loads(output))
                except (ValueError, TypeError):
                    json_results.append(output)

        self._last_value = previous_value

        if output_format == OUTPUT_FORMAT_STR:
            return ""

        import json
        return json.dumps(json_results, indent=2)

    def get_printable(self) -> ResponsePrintable:
        parts = []
        for step in self.content:
            if isinstance(step, AbstractResponse):
                parts.append(step.get_wrapped_printable())
        return os.linesep.join(p for p in parts if p)
