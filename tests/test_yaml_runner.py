import os

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

    def test_env_var_injected(self, kernel):
        """os.environ vars are available as ${VAR} in YAML scripts."""
        from pathlib import Path

        from wexample_wex_core.runner.core_yaml_command_runner import CoreYamlCommandRunner

        os.environ["WEX_TEST_VAR"] = "hello_env"
        runner = CoreYamlCommandRunner(kernel=kernel)
        variables = runner._build_variables({}, Path("/tmp/fake.yml"))

        assert "WEX_TEST_VAR" in variables
        assert variables["WEX_TEST_VAR"] == "hello_env"

    def test_option_overrides_env(self, kernel):
        """Option values take priority over env vars with the same name."""
        from pathlib import Path
        from wexample_wex_core.runner.core_yaml_command_runner import CoreYamlCommandRunner

        os.environ["NAME"] = "from_env"
        runner = CoreYamlCommandRunner(kernel=kernel)
        variables = runner._build_variables({"name": "from_option"}, Path("/tmp/fake.yml"))
        assert variables["NAME"] == "from_option"

    def test_ignore_error_step(self, kernel):
        """ignore_error:true is passed through to the response."""
        from wexample_app.response.interactive_shell_command_response import (
            InteractiveShellCommandResponse,
        )
        from wexample_wex_core.yaml.runners.bash_script_runner import BashScriptRunner

        runner = BashScriptRunner()
        step = {"runner": "bash", "script": "exit 1", "ignore_error": True}
        response = runner.run(step, {}, kernel)

        assert isinstance(response, InteractiveShellCommandResponse)
        assert response.ignore_error is True

    def test_workdir_step(self, kernel):
        """workdir is passed through to the response."""
        from wexample_app.response.interactive_shell_command_response import (
            InteractiveShellCommandResponse,
        )
        from wexample_wex_core.yaml.runners.bash_script_runner import BashScriptRunner

        runner = BashScriptRunner()
        step = {"runner": "bash", "script": "pwd", "workdir": "/tmp"}
        response = runner.run(step, {}, kernel)

        assert isinstance(response, InteractiveShellCommandResponse)
        assert response.workdir == "/tmp"

    def test_workdir_substitution(self, kernel):
        """workdir supports ${VAR} substitution."""
        from wexample_app.response.interactive_shell_command_response import (
            InteractiveShellCommandResponse,
        )
        from wexample_wex_core.yaml.runners.bash_script_runner import BashScriptRunner

        runner = BashScriptRunner()
        step = {"runner": "bash", "script": "pwd", "workdir": "${MY_DIR}"}
        response = runner.run(step, {"MY_DIR": "/tmp"}, kernel)

        assert isinstance(response, InteractiveShellCommandResponse)
        assert response.workdir == "/tmp"
