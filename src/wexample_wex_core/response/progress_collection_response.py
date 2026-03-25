from __future__ import annotations

from typing import TYPE_CHECKING, Any

from wexample_helpers.classes.field import public_field
from wexample_helpers.decorator.base_class import base_class

from wexample_wex_core.response.queued_collection_response import (
    QueuedCollectionResponse,
    _SENTINEL,
)

if TYPE_CHECKING:
    from wexample_prompt.common.progress.progress_handle import ProgressHandle
    from wexample_app.const.types import ResponsePrintable


@base_class
class ProgressCollectionResponse(QueuedCollectionResponse):
    """A QueuedCollectionResponse that displays a progress bar while executing steps.

    For nested ProgressCollectionResponse, sub-progress bars are shown using
    create_range_handle() from the parent handle.
    """

    title: str = public_field(description="Label shown on the progress bar")
    step_labels: list[str] | None = public_field(
        default=None,
        description="Optional label for each step (shown as progress bar updates)",
    )

    def __attrs_post_init__(self) -> None:
        self._execute_super_attrs_post_init_if_exists()
        self._last_value: Any = _SENTINEL
        self._parent_handle: ProgressHandle | None = None

    def _get_step_label(self, index: int) -> str | None:
        if self.step_labels and index < len(self.step_labels):
            return self.step_labels[index]
        return None

    def get_formatted(self, output_format: str) -> str:
        from wexample_app.const.output import OUTPUT_FORMAT_STR
        from wexample_wex_core.response.queue_collection.queued_collection_stop_current_step_response import (
            QueuedCollectionStopCurrentStepResponse,
        )
        from wexample_wex_core.response.queue_collection.queued_collection_stop_response import (
            QueuedCollectionStopResponse,
        )

        total = len(self.content)
        previous_value: Any = None
        json_results: list = []
        handle_finished = False

        # Create progress handle — either sub-progress from parent or new root progress
        if self._parent_handle is not None:
            handle = self._parent_handle.create_range_handle(
                to_step=1, virtual_total=total
            )
        else:
            progress_response = self.kernel.io.progress(
                label=self.title, total=total
            )
            handle = progress_response.get_handle()

        for index, step in enumerate(self.content):
            step_label = self._get_step_label(index)
            is_last = index == total - 1
            response = self._resolve_step(step, previous_value)

            if isinstance(response, QueuedCollectionStopResponse):
                handle.finish()
                handle_finished = True
                break

            if isinstance(response, QueuedCollectionStopCurrentStepResponse):
                if self._parent_handle is not None:
                    handle.advance(step=1)
                else:
                    handle.update(current=index + 1)
                continue

            # Inject parent handle into nested ProgressCollectionResponse
            if isinstance(response, ProgressCollectionResponse):
                self.kernel.io.indentation += 1
                response._parent_handle = handle
                output = response.get_formatted(output_format)
                self.kernel.io.indentation -= 1
            else:
                output = response.get_formatted(output_format)

            previous_value = self._extract_value(response)

            # Use finish() for the last step to avoid double render
            if is_last:
                handle.finish(label=step_label)
                handle_finished = True
            elif self._parent_handle is not None:
                handle.advance(step=1, label=step_label)
            else:
                handle.update(current=index + 1, label=step_label)

            if output_format != OUTPUT_FORMAT_STR and output:
                import json
                try:
                    json_results.append(json.loads(output))
                except (ValueError, TypeError):
                    json_results.append(output)

        if not handle_finished:
            handle.finish()

        self._last_value = previous_value

        if output_format == OUTPUT_FORMAT_STR:
            return ""

        import json
        return json.dumps(json_results, indent=2)

    def get_printable(self) -> ResponsePrintable:
        return self.title
