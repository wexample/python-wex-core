from __future__ import annotations

import shutil
from typing import TYPE_CHECKING

from wexample_helpers.helpers.shell import shell_run

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON
from wexample_wex_core.decorator.command import command

if TYPE_CHECKING:
    from wexample_app.response.dict_response import DictResponse

    from wexample_wex_core.context.execution_context import ExecutionContext


@command(
    type=COMMAND_TYPE_ADDON,
    description="Stop and remove all Docker containers, custom networks, and volumes",
)
def docker__docker__stop_all(context: ExecutionContext) -> DictResponse:
    from wexample_app.response.dict_response import DictResponse

    if shutil.which("docker") is None:
        context.io.warning("Docker is not installed or not available in PATH")
        return DictResponse(
            kernel=context.kernel,
            content={
                "containers_stopped": 0,
                "containers_removed": 0,
                "networks_removed": 0,
                "volumes_removed": 0,
            },
        )

    if not _list_ids(["docker", "info", "--format", "{{.ServerVersion}}"]):
        context.io.warning("Docker does not seem available")
        return DictResponse(
            kernel=context.kernel,
            content={
                "containers_stopped": 0,
                "containers_removed": 0,
                "networks_removed": 0,
                "volumes_removed": 0,
            },
        )

    container_ids = _list_ids(["docker", "ps", "-qa"])
    network_ids = _list_ids(
        ["docker", "network", "ls", "-q", "--filter", "type=custom"]
    )
    volume_ids = _list_ids(["docker", "volume", "ls", "-q"])

    _run_many(["docker", "stop"], container_ids)
    _run_many(["docker", "rm"], container_ids)
    _run_many(["docker", "network", "rm"], network_ids)
    _run_many(["docker", "volume", "rm"], volume_ids)

    context.io.success(
        "Docker cleanup complete "
        f"(containers={len(container_ids)}, networks={len(network_ids)}, volumes={len(volume_ids)})"
    )

    return DictResponse(
        kernel=context.kernel,
        content={
            "containers_stopped": len(container_ids),
            "containers_removed": len(container_ids),
            "networks_removed": len(network_ids),
            "volumes_removed": len(volume_ids),
        },
    )


def _list_ids(command: list[str]) -> list[str]:
    result = shell_run(command, check=False)
    return [line.strip() for line in (result.stdout or "").splitlines() if line.strip()]


def _run_many(base_command: list[str], items: list[str]) -> None:
    if not items:
        return

    shell_run([*base_command, *items], check=False)
