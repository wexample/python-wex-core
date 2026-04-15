from __future__ import annotations

from typing import TYPE_CHECKING, Any

from wexample_wex_core.yaml.abstract_script_runner import AbstractScriptRunner

if TYPE_CHECKING:
    from wexample_wex_core.common.kernel import Kernel


class DockerScriptRunner(AbstractScriptRunner):
    @classmethod
    def get_runner_name(cls) -> str:
        return "docker"

    @classmethod
    def get_step_options(cls) -> list[str]:
        return super().get_step_options() + ["container", "script", "file", "workdir"]

    def run(self, step: dict, variables: dict[str, str], kernel: Kernel) -> Any:
        from wexample_app.response.interactive_shell_command_response import (
            InteractiveShellCommandResponse,
        )

        container: str = step["container"]
        ignore_error: bool = step.get("ignore_error", False)
        workdir: str | None = step.get("workdir")
        script = step.get("script")
        file = step.get("file")

        if script:
            cmd = ["docker", "exec", container, "bash", "-c", script]
        elif file:
            cmd = ["docker", "exec", container, "bash", file]
        else:
            return None

        if workdir:
            cmd = ["docker", "exec", "--workdir", workdir, container] + cmd[3:]

        return InteractiveShellCommandResponse(
            kernel=kernel,
            content=cmd,
            ignore_error=ignore_error,
        )
