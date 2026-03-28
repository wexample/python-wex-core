from __future__ import annotations

from typing import TYPE_CHECKING, Any

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON
from wexample_wex_core.decorator.command import command

if TYPE_CHECKING:
    from wexample_wex_core.context.execution_context import ExecutionContext
    from wexample_wex_core.response.progress_collection_response import ProgressCollectionResponse


@command(type=COMMAND_TYPE_ADDON)
def demo__response__progress(context: ExecutionContext) -> ProgressCollectionResponse:
    import time
    from wexample_app.response.dict_response import DictResponse
    from wexample_wex_core.response.queued_collection_response import QueuedCollectionResponse
    from wexample_wex_core.response.progress_collection_response import ProgressCollectionResponse

    kernel = context.kernel

    def step_init(previous_value: Any) -> dict:
        time.sleep(0.1)
        return {"initialized": True}

    def step_process(previous_value: Any) -> dict:
        time.sleep(0.1)
        return {"processed": previous_value}

    def step_cleanup(previous_value: Any) -> str:
        time.sleep(0.1)
        return "done"

    # Sub-collection with its own progress bar (nested progress)
    sub_progress = ProgressCollectionResponse(
        kernel=kernel,
        title="Sub task",
        step_labels=["Sub step A", "Sub step B"],
        content=[
            lambda previous_value: {"sub_a": True},
            lambda previous_value: {"sub_b": previous_value},
        ],
    )

    # Plain queued collection as a step (no progress bar)
    queued_step = QueuedCollectionResponse(
        kernel=kernel,
        content=[
            DictResponse(kernel=kernel, content={"queued": "step"}),
        ],
    )

    return ProgressCollectionResponse(
        kernel=kernel,
        title="@color:cyan+bold{Running demo}",
        step_labels=["Initializing", "Sub task", "Queued step", "Processing", "Cleanup"],
        content=[
            step_init,
            sub_progress,
            queued_step,
            step_process,
            step_cleanup,
        ],
    )
