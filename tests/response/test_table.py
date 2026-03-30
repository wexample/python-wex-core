from __future__ import annotations

import json

from wexample_app.const.output import (
    OUTPUT_FORMAT_JSON,
    OUTPUT_FORMAT_STR,
    OUTPUT_TARGET_NONE,
)
from wexample_app.response.table_response import TableResponse

from tests.response.abstract_response_test import AbstractResponseTest


class TestTableResponse(AbstractResponseTest):
    def create_response(self, kernel) -> TableResponse:
        return TableResponse(
            kernel=kernel,
            headers=["name", "value"],
            content=[["alpha", "1"], ["beta", "2"]],
        )

    def get_command(self):
        from wexample_wex_core.addons.demo.commands.ping.pong import demo__ping__pong

        return demo__ping__pong

    def get_command_arguments(self) -> dict:
        return {"type": "table"}

    def test_json_contains_headers_and_rows(self, kernel) -> None:
        output = self.create_response(kernel).get_formatted(OUTPUT_FORMAT_JSON)
        data = json.loads(output)

        assert data["headers"] == ["name", "value"]
        assert data["rows"] == [["alpha", "1"], ["beta", "2"]]

    def test_ping_response_has_headers(self, kernel) -> None:
        response = kernel.execute_kernel_command(
            self._make_request(kernel, output_target=[OUTPUT_TARGET_NONE])
        )
        assert response.headers == ["name", "status"]
        assert len(response.content) == 2

    def test_ping_returns_table_response(self, kernel) -> None:
        response = kernel.execute_kernel_command(
            self._make_request(kernel, output_target=[OUTPUT_TARGET_NONE])
        )
        assert isinstance(response, TableResponse)

    def test_str_contains_headers_and_cells(self, kernel, capsys) -> None:
        self.create_response(kernel).get_formatted(OUTPUT_FORMAT_STR)
        out = capsys.readouterr().out

        assert "name" in out
        assert "value" in out
        assert "alpha" in out
        assert "beta" in out

    def test_str_empty(self, kernel, capsys) -> None:
        TableResponse(kernel=kernel, content=[]).get_formatted(OUTPUT_FORMAT_STR)
        out = capsys.readouterr().out

        assert out == "" or out.strip() == ""

    def test_str_with_title(self, kernel, capsys) -> None:
        TableResponse(
            kernel=kernel,
            headers=["col"],
            content=[["val"]],
            title="My title",
        ).get_formatted(OUTPUT_FORMAT_STR)
        out = capsys.readouterr().out

        assert "My title" in out
        assert "col" in out
        assert "val" in out
