from __future__ import annotations

import json
import os
from typing import TYPE_CHECKING, Any

from wexample_helpers.classes.field import public_field
from wexample_helpers.decorator.base_class import base_class

from wexample_app.response.abstract_response import AbstractResponse

if TYPE_CHECKING:
    from wexample_prompt.responses.abstract_prompt_response import AbstractPromptResponse
    from wexample_app.const.types import ResponsePrintable


@base_class
class TableResponse(AbstractResponse):
    content: list[list[Any]] = public_field(description="Table rows, each row a list of cell values")
    headers: list[str] | None = public_field(default=None, description="Optional column headers")
    title: str | None = public_field(default=None, description="Optional table title")

    def get_printable(self) -> ResponsePrintable:
        lines = []
        if self.title:
            lines.append(self.title)
        if self.headers:
            lines.append(" | ".join(self.headers))
        for row in self.content:
            lines.append(" | ".join(str(cell) for cell in row))
        return os.linesep.join(lines)

    def _get_formatted_json_content(self) -> str:
        return json.dumps({"headers": self.headers, "rows": self.content}, indent=2)

    def _get_formatted_prompt_response(self) -> AbstractPromptResponse | None:
        from wexample_prompt.responses.data.table_prompt_response import TablePromptResponse

        return TablePromptResponse.create_table(
            data=self.content,
            headers=self.headers,
            title=self.title,
        )
