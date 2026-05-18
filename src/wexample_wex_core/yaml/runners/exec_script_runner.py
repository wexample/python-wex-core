from __future__ import annotations

from typing import TYPE_CHECKING, Any

from wexample_wex_core.yaml.abstract_script_runner import AbstractScriptRunner

if TYPE_CHECKING:
    from wexample_wex_core.common.kernel import Kernel


class ExecScriptRunner(AbstractScriptRunner):
    """Execute a script step with an arbitrary interpreter.

    Example::

        - runner: exec
          interpreter: [node, -e]
          script: console.log("hello from node")

        - runner: exec
          interpreter: [ruby, -e]
          script: puts "hello"

        - runner: exec
          interpreter: [php, -r]
          script: echo "hello";

    ``interpreter`` must be a list — the script is appended as the last argument.
    """

    @classmethod
    def get_runner_name(cls) -> str:
        return "exec"

    @classmethod
    def get_step_options(cls) -> list[str]:
        return super().get_step_options() + ["interpreter", "script"]

    def run(self, step: dict, variables: dict[str, str], kernel: Kernel) -> Any:
        from wexample_app.response.interactive_shell_command_response import (
            InteractiveShellCommandResponse,
        )

        interpreter = step.get("interpreter")
        script = step.get("script")

        if not interpreter:
            raise ValueError("exec runner requires 'interpreter' (e.g. [node, -e]).")
        if not isinstance(interpreter, list):
            raise ValueError("exec runner: 'interpreter' must be a list.")
        if not script:
            raise ValueError("exec runner requires 'script'.")

        cmd = interpreter + [script]

        return InteractiveShellCommandResponse(
            kernel=kernel,
            content=cmd,
            ignore_error=step.get("ignore_error", False),
        )
