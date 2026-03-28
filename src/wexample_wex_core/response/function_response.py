from __future__ import annotations

from typing import TYPE_CHECKING, Any

from wexample_helpers.classes.field import public_field
from wexample_helpers.decorator.base_class import base_class

from wexample_app.response.abstract_response import AbstractResponse

if TYPE_CHECKING:
    from wexample_app.const.types import ResponsePrintable


@base_class
class FunctionResponse(AbstractResponse):
    """Execute a command function and expose its response.

    Useful to return a function call as a response without wrapping
    it in a QueuedCollectionResponse.
    """

    content: Any = public_field(
        description="CommandMethodWrapper to execute"
    )
    arguments: dict = public_field(
        factory=dict,
        description="Arguments passed to the function",
    )

    def __attrs_post_init__(self) -> None:
        self._execute_super_attrs_post_init_if_exists()
        self._inner_response: AbstractResponse | None = None

    def _get_inner_response(self) -> AbstractResponse:
        if self._inner_response is None:
            self._inner_response = self.kernel.run_function(self.content, self.arguments)
        return self._inner_response

    def get_formatted(self, output_format: str) -> str:
        return self._get_inner_response().get_formatted(output_format)

    def get_printable(self) -> ResponsePrintable:
        return self._get_inner_response().get_printable()
