from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Callable

from wexample_helpers.classes.field import public_field
from wexample_helpers.decorator.base_class import base_class

from wexample_app.response.abstract_response import AbstractResponse

if TYPE_CHECKING:
    from wexample_app.const.types import ResponsePrintable

# A step can be a response, a callable, or a plain value
QueueStep = AbstractResponse | Callable | Any


@base_class
class QueuedCollectionResponse(AbstractResponse):
    """Execute a list of steps sequentially.

    Each step is executed in order. If a step returns or is a
    QueuedCollectionStopResponse, the queue halts entirely.
    If a step returns QueuedCollectionStopCurrentStepResponse, that step
    is skipped and the queue continues.

    Callable steps receive `previous_value` as keyword argument if their
    signature accepts it, allowing pipelines where each step uses the
    previous result.
    """

    content: list[QueueStep] = public_field(
        default_factory=list,
        description="Ordered list of steps to execute sequentially",
    )

    def _resolve_step(self, step: QueueStep, previous_value: Any) -> AbstractResponse:
        """Normalize a step into an AbstractResponse."""
        from wexample_helpers.helpers.args import args_in_function

        from wexample_app.helpers.response import response_normalize
        from wexample_wex_core.response.queue_collection.queued_collection_stop_current_step_response import (
            QueuedCollectionStopCurrentStepResponse,
        )

        if callable(step):
            kwargs = {}
            if args_in_function(step, "previous_value"):
                kwargs["previous_value"] = previous_value
            result = step(**kwargs)
            return response_normalize(kernel=self.kernel, response=result)

        if isinstance(step, AbstractResponse):
            return step

        return response_normalize(kernel=self.kernel, response=step)

    def get_formatted(self, output_format: str) -> str:
        from wexample_app.const.output import OUTPUT_FORMAT_STR
        from wexample_wex_core.response.queue_collection.queued_collection_stop_response import (
            QueuedCollectionStopResponse,
        )
        from wexample_wex_core.response.queue_collection.queued_collection_stop_current_step_response import (
            QueuedCollectionStopCurrentStepResponse,
        )

        previous_value: Any = None
        results: list[str] = []

        for step in self.content:
            response = self._resolve_step(step, previous_value)

            if isinstance(response, QueuedCollectionStopResponse):
                break

            if isinstance(response, QueuedCollectionStopCurrentStepResponse):
                continue

            output = response.get_formatted(output_format)
            previous_value = response.content

            if output_format != OUTPUT_FORMAT_STR:
                results.append(output)

        if output_format == OUTPUT_FORMAT_STR:
            return ""

        import json
        return json.dumps(results, indent=2)

    def get_printable(self) -> ResponsePrintable:
        # Fallback: join printable of each step (used when get_formatted is not called)
        parts = []
        for step in self.content:
            if isinstance(step, AbstractResponse):
                parts.append(step.get_wrapped_printable())
        return os.linesep.join(p for p in parts if p)
