import json

import pytest

from wexample_app.const.output import OUTPUT_FORMAT_JSON, OUTPUT_FORMAT_STR, OUTPUT_TARGET_NONE
from wexample_app.response.dict_response import DictResponse

from tests.response.abstract_response_test import AbstractResponseTest


class TestDictResponse(AbstractResponseTest):
    def create_response(self, kernel) -> DictResponse:
        return DictResponse(kernel=kernel, content={"color": "red", "size": "large"})

    def get_command(self):
        from wexample_wex_core.addons.demo.commands.ping.pong import demo__ping__pong

        return demo__ping__pong

    def get_command_arguments(self) -> dict:
        return {"type": "dict"}


    def test_str_contains_keys_and_values(self, kernel, capsys):
        self.create_response(kernel).get_formatted(OUTPUT_FORMAT_STR)
        out = capsys.readouterr().out

        assert "color" in out
        assert "red" in out
        assert "size" in out
        assert "large" in out

    def test_str_with_title(self, kernel, capsys):
        DictResponse(kernel=kernel, content={"color": "red"}, title="My title").get_formatted(OUTPUT_FORMAT_STR)
        out = capsys.readouterr().out

        assert "My title" in out
        assert "color" in out
        assert "red" in out

    def test_str_nested(self, kernel, capsys):
        DictResponse(kernel=kernel, content={"outer": {"inner": "value"}}).get_formatted(OUTPUT_FORMAT_STR)
        out = capsys.readouterr().out

        assert "outer" in out
        assert "inner" in out
        assert "value" in out

    def test_str_empty(self, kernel, capsys):
        DictResponse(kernel=kernel, content={}).get_formatted(OUTPUT_FORMAT_STR)
        out = capsys.readouterr().out

        assert out == "" or out.strip() == ""

    def test_json_exact_content(self, kernel):
        output = self.create_response(kernel).get_formatted(OUTPUT_FORMAT_JSON)
        assert json.loads(output) == {"color": "red", "size": "large"}

    def test_ping_returns_dict_response(self, kernel):
        response = kernel.execute_kernel_command(self._make_request(kernel, output_target=[OUTPUT_TARGET_NONE]))
        assert isinstance(response, DictResponse)

    def test_ping_response_content(self, kernel):
        response = kernel.execute_kernel_command(self._make_request(kernel, output_target=[OUTPUT_TARGET_NONE]))
        assert response.content == {"status": "pong"}
