from __future__ import annotations

import platform
import shutil
import socket
import subprocess
from typing import TYPE_CHECKING

from wexample_cli.decorator.command import command
from wexample_cli.const.tags import AudienceTag, EffectTag, ScopeTag
from wexample_wex_core.addons.docker.const.tags import DomainTag
from wexample_helpers.helpers.shell import shell_run

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON

if TYPE_CHECKING:
    from wexample_cli.context.execution_context import ExecutionContext

_DEFAULT_LOCAL_IP = "127.0.1.1"


@command(type=COMMAND_TYPE_ADDON, description="Return the current Docker local IP",
    tags=[
        DomainTag.CONTAINER,
        DomainTag.DOCKER,
        DomainTag.SYSTEM,
        EffectTag.READ_ONLY,
        EffectTag.SUBPROCESS_SPAWN,
        AudienceTag.AGENT_SAFE,
        ScopeTag.HOST,
        ScopeTag.LOCAL,
    ],
)
def docker__network__ip(context: ExecutionContext) -> str:
    if platform.system() == "Darwin":
        return "127.0.0.1"

    if shutil.which("docker-machine"):
        try:
            result = shell_run(["docker-machine", "ip"])
            ip = (result.stdout or "").strip()
            if ip:
                return ip
        except subprocess.CalledProcessError:
            pass

    try:
        return socket.gethostbyname(socket.gethostname())
    except OSError:
        return _DEFAULT_LOCAL_IP
