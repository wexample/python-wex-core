from __future__ import annotations

from typing import TYPE_CHECKING, Any

from wexample_wex_core.yaml.abstract_script_runner import AbstractScriptRunner

if TYPE_CHECKING:
    from wexample_wex_core.common.kernel import Kernel


class DockerScriptRunner(AbstractScriptRunner):
    """Execute a script step inside a Docker container.

    Two ways to target a container:

    ``service: main``
        Short service name — expanded to the full container name using the
        current app workdir (e.g. ``wex_apt_repo_local_main``).
        Falls back to the literal value if no app context is found.

    ``container: wex_apt_repo_local_main``
        Explicit full container name — used verbatim, no expansion.
    """

    @classmethod
    def get_runner_name(cls) -> str:
        return "docker"

    @classmethod
    def get_step_options(cls) -> list[str]:
        return super().get_step_options() + [
            "service",
            "container",
            "script",
            "file",
            "workdir",
        ]

    def run(self, step: dict, variables: dict[str, str], kernel: Kernel) -> Any:
        from wexample_app.response.interactive_shell_command_response import (
            InteractiveShellCommandResponse,
        )

        service: str | None = step.get("service")
        container: str | None = step.get("container")

        if not service and not container:
            raise ValueError(
                "Docker runner requires either 'service' (short name) or 'container' (full name)."
            )

        if service:
            container = self._resolve_service_name(service, kernel)
        # container is guaranteed non-None past this point

        ignore_error: bool = step.get("ignore_error", False)
        workdir: str | None = step.get("workdir")
        script = step.get("script")
        file = step.get("file")

        if script:
            inner = ["bash", "-c", script]
        elif file:
            inner = ["bash", file]
        else:
            return None

        # CI=true disables interactive spinners and prompts in most modern CLI tools
        # (drizzle-kit, bun, vite, jest, etc.) that detect isatty()=false in docker exec.
        exec_cmd = ["docker", "exec", "--env", "CI=true"]
        if workdir:
            exec_cmd += ["--workdir", workdir]
        exec_cmd.append(container)
        cmd = exec_cmd + inner

        return InteractiveShellCommandResponse(
            kernel=kernel,
            content=cmd,
            ignore_error=ignore_error,
        )

    @staticmethod
    def _resolve_service_name(service: str, kernel: Kernel) -> str:
        """Expand a short service name to the full Docker container name.

        Queries all registered addons via get_docker_service_name().
        The first addon that returns a non-None value "wins".
        Falls back to the literal service name if no addon can resolve it.
        """
        for addon in kernel.get_addons().values():
            result = addon.get_service_docker_container_name(service)
            if result is not None:
                return result

        return service
