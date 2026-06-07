from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

from wexample_cli.const.tags import AudienceTag, EffectTag, ScopeTag
from wexample_cli.decorator.command import command

from wexample_wex_core.addons.system.const.tags import DomainTag
from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON

if TYPE_CHECKING:
    from wexample_cli.context.execution_context import ExecutionContext


@command(
    type=COMMAND_TYPE_ADDON,
    description="Return true if the current environment is a Docker container",
    tags=[
        DomainTag.SYSTEM,
        EffectTag.IDEMPOTENT,
        EffectTag.READ_ONLY,
        AudienceTag.AGENT_SAFE,
        ScopeTag.HOST,
        ScopeTag.LOCAL,
    ],
)
def system__runtime__is_docker(context: ExecutionContext) -> bool:
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
