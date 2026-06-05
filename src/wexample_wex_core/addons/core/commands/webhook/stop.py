from __future__ import annotations

from typing import TYPE_CHECKING

import psutil
from wexample_cli.decorator.command import command
from wexample_cli.decorator.option import option
from wexample_cli.const.tags import AudienceTag, EffectTag, ScopeTag
from wexample_wex_core.addons.core.const.tags import DomainTag

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON
from wexample_wex_core.webhook.const import WEBHOOK_LISTEN_PORT_DEFAULT

if TYPE_CHECKING:
    from wexample_cli.context.execution_context import ExecutionContext


@option(
    "port",
    type=int,
    short_name="p",
    required=False,
    default=WEBHOOK_LISTEN_PORT_DEFAULT,
    description="Port the daemon is listening on",
)
@command(type=COMMAND_TYPE_ADDON, description="Stop the webhook daemon",
    tags=[
        DomainTag.CORE,
        DomainTag.HTTP,
        DomainTag.WEBHOOK,
        EffectTag.DESTRUCTIVE,
        EffectTag.WRITE,
        AudienceTag.DANGEROUS,
        ScopeTag.GLOBAL,
        ScopeTag.LOCAL,
    ],
)
def core__webhook__stop(
    context: ExecutionContext,
    port: int = WEBHOOK_LISTEN_PORT_DEFAULT,
):
    from wexample_app.response.success_response import SuccessResponse

    from wexample_wex_core.addons.system.helpers import system_find_process_by_port

    proc = system_find_process_by_port(port)

    if not proc:
        return f"No webhook daemon found on port {port}"

    pid = proc.pid
    context.io.log(f"Stopping webhook daemon on port {port} (pid {pid})...")

    try:
        proc.terminate()
        proc.wait(timeout=5)
        return SuccessResponse(
            kernel=context.kernel, message=f"Daemon stopped (pid {pid})"
        )
    except psutil.TimeoutExpired:
        proc.kill()
        return SuccessResponse(
            kernel=context.kernel, message=f"Daemon force-killed (pid {pid})"
        )
    except psutil.NoSuchProcess:
        return f"Process {pid} already gone"
