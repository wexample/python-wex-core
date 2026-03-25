from __future__ import annotations

from typing import TYPE_CHECKING, Any

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON
from wexample_wex_core.decorator.command import command

if TYPE_CHECKING:
    from wexample_wex_core.context.execution_context import ExecutionContext
    from wexample_wex_core.response.queued_collection_response import QueuedCollectionResponse

DEMO_COLLECTION_FIRST_VALUE = "first-function-result"


@command(type=COMMAND_TYPE_ADDON)
def demo__response__collection(context: ExecutionContext) -> QueuedCollectionResponse:
    from wexample_wex_core.response.dict_response import DictResponse
    from wexample_wex_core.response.list_response import ListResponse
    from wexample_wex_core.response.queued_collection_response import QueuedCollectionResponse

    kernel = context.kernel

    def step_first(previous_value: Any) -> str:
        return DEMO_COLLECTION_FIRST_VALUE

    def step_second(previous_value: Any) -> dict:
        return {"previous": previous_value, "current": "second"}

    def step_third(previous_value: Any) -> dict:
        assert isinstance(previous_value, dict)
        return {"keys": list(previous_value.keys()), "count": len(previous_value)}

    def step_sub_collection(previous_value: Any) -> QueuedCollectionResponse:
        return QueuedCollectionResponse(
            kernel=kernel,
            content=[
                "sub-step-one",
                "sub-step-two",
                lambda previous_value: {"from_sub": previous_value},
            ],
        )

    def step_after_sub(previous_value: Any) -> dict:
        return {"after_sub": str(previous_value)}

    return QueuedCollectionResponse(
        kernel=kernel,
        content=[
            # Plain values
            "simple-string",
            42,
            ["list-item-a", "list-item-b"],
            {"simple": "dict"},
            # Callables with previous_value chaining
            step_first,
            step_second,
            step_third,
            # Response objects
            DictResponse(kernel=kernel, content={"inline": "response"}),
            ListResponse(kernel=kernel, content=["inline", "list"]),
            # Nested QueuedCollectionResponse
            step_sub_collection,
            step_after_sub,
        ],
    )
