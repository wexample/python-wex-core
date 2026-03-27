from wexample_app.const.output import OUTPUT_FORMAT_JSON, OUTPUT_FORMAT_STR

from tests.abstract_kernel_test import AbstractKernelTest
from wexample_wex_core.response.shell_command_response import ShellCommandResponse
from wexample_wex_core.response.interactive_shell_command_response import InteractiveShellCommandResponse


class TestShellCommandResponse(AbstractKernelTest):
    def test_captures_output(self, kernel):
        response = ShellCommandResponse(
            kernel=kernel, content=["echo", "hello world"]
        )
        assert response.get_formatted(OUTPUT_FORMAT_STR) == "hello world"

    def test_json_format(self, kernel):
        import json
        response = ShellCommandResponse(kernel=kernel, content=["echo", "hi"])
        result = json.loads(response.get_formatted(OUTPUT_FORMAT_JSON))
        assert result["output"] == "hi"
        assert result["returncode"] == 0

    def test_ignore_error(self, kernel):
        response = ShellCommandResponse(
            kernel=kernel,
            content=["false"],
            ignore_error=True,
        )
        response.get_formatted(OUTPUT_FORMAT_STR)
        assert response._returncode != 0

    def test_string_command(self, kernel):
        response = ShellCommandResponse(kernel=kernel, content="echo hello")
        assert response.get_formatted(OUTPUT_FORMAT_STR) == "hello"

    def test_interactive_runs(self, kernel):
        response = InteractiveShellCommandResponse(
            kernel=kernel, content=["echo", "interactive"]
        )
        # Output goes directly to the terminal fd — not capturable via capsys.
        # Just verify it executes without error and returns "".
        assert response.get_formatted(OUTPUT_FORMAT_STR) == ""
