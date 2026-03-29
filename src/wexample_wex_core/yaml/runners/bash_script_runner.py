from __future__ import annotations

from typing import TYPE_CHECKING, Any

from wexample_wex_core.yaml.abstract_script_runner import AbstractScriptRunner

if TYPE_CHECKING:
    from wexample_wex_core.common.kernel import Kernel
    from wexample_wex_core.yaml.types import BashStepDict


class BashScriptRunner(AbstractScriptRunner):
    @classmethod
    def get_runner_name(cls) -> str:
        return "bash"

    @classmethod
    def get_step_options(cls) -> list[str]:
        return super().get_step_options() + ["script", "file", "workdir"]

    def run(self, step: BashStepDict, variables: dict[str, str], kernel: Kernel) -> Any:
        from wexample_app.response.interactive_shell_command_response import (
            InteractiveShellCommandResponse,
        )

        # step strings are already substituted by the time run() is called
        ignore_error: bool = step.get("ignore_error", False)
        workdir: str | None = step.get("workdir")
        script = step.get("script")
        file = step.get("file")

        if script:
            return InteractiveShellCommandResponse(
                kernel=kernel,
                content=["bash", "-c", script],
                ignore_error=ignore_error,
                workdir=workdir,
            )
        elif file:
            return InteractiveShellCommandResponse(
                kernel=kernel,
                content=["bash", file],
                ignore_error=ignore_error,
                workdir=workdir,
            )

        return None
