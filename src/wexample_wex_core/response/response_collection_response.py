from __future__ import annotations

import json
import os
from typing import TYPE_CHECKING

from wexample_helpers.classes.field import public_field
from wexample_helpers.decorator.base_class import base_class

from wexample_app.response.abstract_response import AbstractResponse

if TYPE_CHECKING:
    from wexample_app.const.types import ResponsePrintable


@base_class
class ResponseCollectionResponse(AbstractResponse):
    content: list[AbstractResponse] = public_field(
        default_factory=list,
        description="Ordered list of responses to render sequentially",
    )

    def get_printable(self) -> ResponsePrintable:
        return os.linesep.join(r.get_wrapped_printable() for r in self.content)

    def get_formatted(self, output_format: str) -> str:
        from wexample_app.const.output import OUTPUT_FORMAT_STR

        if output_format == OUTPUT_FORMAT_STR:
            for response in self.content:
                response.get_formatted(output_format)
            return ""

        return super().get_formatted(output_format)

    def _get_formatted_json_content(self) -> str:
        items = [json.loads(r._get_formatted_json_content()) for r in self.content]
        return json.dumps(items, indent=2)
