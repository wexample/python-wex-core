from __future__ import annotations

import json

from wexample_app.const.output import (
    OUTPUT_FORMAT_JSON,
    OUTPUT_FORMAT_STR,
    OUTPUT_TARGET_NONE,
)
from wexample_app.response.list_response import ListResponse

from tests.response.abstract_response_test import AbstractResponseTest


class TestListResponse(AbstractResponseTest):
    def create_response(self, kernel) -> ListResponse:
        return ListResponse(kernel=kernel, content=["alpha", "beta", "gamma"])

    def get_command(self):
        from wexample_wex_core.addons.demo.commands.ping.pong import demo__ping__pong

        return demo__ping__pong

    def get_command_arguments(self) -> dict:
        return {"type": "list"}

    def test_json_exact_content(self, kernel) -> None:
        output = self.create_response(kernel).get_formatted(OUTPUT_FORMAT_JSON)
        assert json.loads(output) == ["alpha", "beta", "gamma"]

    def test_ping_response_content(self, kernel) -> None:
        response = kernel.execute_kernel_command(
            self._make_request(kernel, output_target=[OUTPUT_TARGET_NONE])
        )
        assert response.content == ["pong", "ping", "pang"]

    def test_ping_returns_list_response(self, kernel) -> None:
        response = kernel.execute_kernel_command(
            self._make_request(kernel, output_target=[OUTPUT_TARGET_NONE])
        )
        assert isinstance(response, ListResponse)

    def test_str_contains_items(self, kernel) -> None:
        out = self.create_response(kernel).get_formatted(OUTPUT_FORMAT_STR)

        assert "alpha" in out
        assert "beta" in out
        assert "gamma" in out

    def test_str_empty(self, kernel) -> None:
        out = ListResponse(kernel=kernel, content=[]).get_formatted(OUTPUT_FORMAT_STR)

        assert out == "" or out.strip() == ""

    def test_str_with_title(self, kernel) -> None:
        out = ListResponse(
            kernel=kernel, content=["alpha"], title="My title"
        ).get_formatted(OUTPUT_FORMAT_STR)

        assert "My title" in out
        assert "alpha" in out
