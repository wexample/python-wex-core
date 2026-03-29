import json

import pytest
import yaml

from wexample_app.const.output import (
    OUTPUT_FORMAT_JSON,
    OUTPUT_FORMAT_STR,
    OUTPUT_FORMAT_YAML,
    OUTPUT_TARGET_STDOUT,
)

from tests.abstract_kernel_test import AbstractKernelTest


class TestOutputFormatEndToEnd(AbstractKernelTest):
    """End-to-end tests: output_format flows through request → output handler → stdout.

    Tests the chain: CommandRequest.output_format → AbstractAppOutputHandler.print()
    → response.get_formatted() → stdout.

    Uses the output handler directly (not execute_kernel_command_and_print) to avoid
    @attach hook logs mixing with structured output.
    """

    def _run(self, kernel, capsys, output_format: str) -> str:
        from wexample_app.output.app_stdout_output_handler import AppStdoutOutputHandler
        from wexample_app.response.dict_response import DictResponse
        from wexample_wex_core.common.command_request import CommandRequest

        response = DictResponse(kernel=kernel, content={"status": "pong"})
        request = CommandRequest(
            kernel=kernel,
            name="demo::ping/pong",
            output_target=[OUTPUT_TARGET_STDOUT],
            output_format=output_format,
            arguments={},
        )
        handler = AppStdoutOutputHandler(kernel=kernel)
        handler.print(request=request, response=response)
        return capsys.readouterr().out

    def test_end_to_end_str_format(self, kernel, capsys):
        out = self._run(kernel, capsys, OUTPUT_FORMAT_STR)
        assert "status" in out
        assert "pong" in out

    def test_end_to_end_json_format(self, kernel, capsys):
        out = self._run(kernel, capsys, OUTPUT_FORMAT_JSON)
        parsed = json.loads(out)
        assert parsed == {"status": "pong"}

    def test_end_to_end_yaml_format(self, kernel, capsys):
        out = self._run(kernel, capsys, OUTPUT_FORMAT_YAML)
        parsed = yaml.safe_load(out)
        assert parsed is not None
        assert parsed.get("status") == "pong"
