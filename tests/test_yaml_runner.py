import os

import pytest

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

    def test_python_runner_returns_lazy_response(self, kernel):
        """Python runner returns a PythonScriptResponse, not executing immediately."""
        from wexample_wex_core.yaml.python_script_response import PythonScriptResponse
        from wexample_wex_core.yaml.runners.python_script_runner import PythonScriptRunner

        runner = PythonScriptRunner()
        step = {"runner": "python", "script": "x = 1 + 1"}
        response = runner.run(step, {}, kernel)

        assert isinstance(response, PythonScriptResponse)
        assert response._executed is False  # not yet run

    def test_python_runner_error_raised_at_render(self, kernel):
        """Python script errors surface at render time, not at build time."""
        from wexample_app.const.output import OUTPUT_FORMAT_STR
        from wexample_wex_core.yaml.runners.python_script_runner import PythonScriptRunner

        runner = PythonScriptRunner()
        step = {"runner": "python", "script": "raise ValueError('boom')"}
        response = runner.run(step, {}, kernel)

        assert response is not None  # build succeeded — no error yet

        with pytest.raises(ValueError, match="boom"):
            response.get_formatted(OUTPUT_FORMAT_STR)

    def test_python_runner_ignore_error(self, kernel):
        """ignore_error:true silences Python exceptions."""
        from wexample_app.const.output import OUTPUT_FORMAT_STR
        from wexample_wex_core.yaml.runners.python_script_runner import PythonScriptRunner

        runner = PythonScriptRunner()
        step = {"runner": "python", "script": "raise ValueError('boom')", "ignore_error": True}
        response = runner.run(step, {}, kernel)

        # No exception raised
        response.get_formatted(OUTPUT_FORMAT_STR)

    def test_step_options_contract(self, kernel):
        """Each runner declares its supported options; ignore_error is universal."""
        from wexample_wex_core.yaml.runners.bash_script_runner import BashScriptRunner
        from wexample_wex_core.yaml.runners.python_script_runner import PythonScriptRunner

        assert "ignore_error" in BashScriptRunner.get_step_options()
        assert "ignore_error" in PythonScriptRunner.get_step_options()
        assert "workdir" in BashScriptRunner.get_step_options()
        assert "workdir" not in PythonScriptRunner.get_step_options()

    def test_workdir_substitution(self, kernel):
        """${VAR} in workdir is substituted globally before the runner is called."""
        from wexample_wex_core.yaml.yaml_variable import yaml_substitute_step

        step = {"runner": "bash", "script": "pwd", "workdir": "${MY_DIR}"}
        substituted = yaml_substitute_step(step, {"MY_DIR": "/tmp"})

        assert substituted["workdir"] == "/tmp"
        assert substituted["script"] == "pwd"
