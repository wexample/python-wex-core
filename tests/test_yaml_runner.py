from wexample_app.const.output import OUTPUT_TARGET_NONE

from tests.abstract_kernel_test import AbstractKernelTest


class TestYamlRunner(AbstractKernelTest):
    def test_yaml_command_in_registry(self, kernel):
        addon_commands = kernel.get_configuration_registry().get_addon_commands()
        assert "demo" in addon_commands
        assert "yaml/hello" in addon_commands["demo"]

    def test_yaml_command_has_description(self, kernel):
        addon_commands = kernel.get_configuration_registry().get_addon_commands()
        cmd = addon_commands["demo"]["yaml/hello"]
        assert cmd.get("description") == "Demo YAML command — prints a greeting using a bash script"

    def test_yaml_command_executes_default(self, kernel):
        from io import StringIO
        from unittest.mock import patch

        from wexample_wex_core.common.command_request import CommandRequest

        request = CommandRequest(
            kernel=kernel,
            name="demo::yaml/hello",
            output_target=[OUTPUT_TARGET_NONE],
            arguments={},
        )

        with patch("sys.stdout", new_callable=StringIO) as mock_out:
            response = kernel.execute_kernel_command(request)

        assert response is not None

    def test_yaml_command_executes_with_name(self, kernel):
        from wexample_app.response.interactive_shell_command_response import (
            InteractiveShellCommandResponse,
        )

        from wexample_wex_core.common.command_request import CommandRequest

        request = CommandRequest(
            kernel=kernel,
            name="demo::yaml/hello",
            output_target=[OUTPUT_TARGET_NONE],
            arguments={"name": "Wex"},
        )

        response = kernel.execute_kernel_command(request)

        assert isinstance(response, InteractiveShellCommandResponse)
