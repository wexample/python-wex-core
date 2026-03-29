from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON
from wexample_wex_core.decorator.command import command

if TYPE_CHECKING:
    from wexample_wex_core.context.execution_context import ExecutionContext


@command(type=COMMAND_TYPE_ADDON, description="Return true if the current environment is a Docker container")
def system__system__is_docker(context: "ExecutionContext") -> bool:
    # Standard Docker indicator
    if Path("/.dockerenv").exists():
        return True
    # Explicit env var override
    if os.environ.get("DOCKER_RUNNING"):
        return True
    # Check cgroup for docker/containerd signatures
    try:
        cgroup = Path("/proc/1/cgroup").read_text()
        return "docker" in cgroup or "containerd" in cgroup
    except OSError:
        return False
