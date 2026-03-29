from __future__ import annotations

from typing import TYPE_CHECKING, Any

from wexample_wex_core.yaml.abstract_script_runner import AbstractScriptRunner

if TYPE_CHECKING:
    from wexample_wex_core.common.kernel import Kernel


class BashScriptRunner(AbstractScriptRunner):
    @classmethod
    def get_runner_name(cls) -> str:
        return "bash"

    def run(self, step: dict, variables: dict[str, str], kernel: Kernel) -> Any:
        from wexample_app.response.interactive_shell_command_response import (
            InteractiveShellCommandResponse,
        )
        from wexample_wex_core.yaml.yaml_variable import yaml_substitute

        script = step.get("script")
        file = step.get("file")

        ignore_error: bool = step.get("ignore_error", False)
        workdir: str | None = step.get("workdir")
        if workdir:
            workdir = yaml_substitute(workdir, variables)

        if script:
            return InteractiveShellCommandResponse(
                kernel=kernel,
                content=["bash", "-c", yaml_substitute(script, variables)],
                ignore_error=ignore_error,
                workdir=workdir,
            )
        elif file:
            return InteractiveShellCommandResponse(
                kernel=kernel,
                content=["bash", yaml_substitute(file, variables)],
                ignore_error=ignore_error,
                workdir=workdir,
            )

        return None
