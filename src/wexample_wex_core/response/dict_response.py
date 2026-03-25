from __future__ import annotations

import json
import os
from typing import TYPE_CHECKING

from wexample_helpers.classes.field import public_field
from wexample_helpers.decorator.base_class import base_class

from wexample_app.response.abstract_response import AbstractResponse

if TYPE_CHECKING:
    from wexample_prompt.responses.abstract_prompt_response import AbstractPromptResponse
    from wexample_app.const.types import ResponsePrintable


@base_class
class DictResponse(AbstractResponse):
    content: dict = public_field(description="Dictionary content to display")
    title: str | None = public_field(default=None, description="Optional section title")

    def get_printable(self) -> ResponsePrintable:
        lines = []
        if self.title:
            lines.append(self.title)
        for key, value in self.content.items():
            lines.append(f"{key}: {value}")
        return os.linesep.join(lines)

    def _get_formatted_json_content(self) -> str:
        return json.dumps(self.content, indent=2)

    def _get_formatted_prompt_response(self) -> AbstractPromptResponse | None:
        from wexample_prompt.responses.data.properties_prompt_response import PropertiesPromptResponse

        return PropertiesPromptResponse.create_properties(
            properties=self.content,
            title=self.title,
        )
