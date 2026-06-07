from __future__ import annotations

from typing import TYPE_CHECKING

import psutil
from wexample_cli.const.tags import AudienceTag, EffectTag, ScopeTag
from wexample_cli.decorator.as_sudo import as_sudo
from wexample_cli.decorator.command import command
from wexample_cli.decorator.option import option

from wexample_wex_core.addons.system.const.tags import DomainTag
from wexample_wex_core.addons.system.helpers import system_find_process_by_port
from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON

if TYPE_CHECKING:
    from wexample_cli.context.execution_context import ExecutionContext


@option("port", type=int, short_name="p", required=True, description="Port number")
@as_sudo()
@command(
    type=COMMAND_TYPE_ADDON,
    description="Kill the process listening on a port",
    tags=[
        DomainTag.PROCESS,
        DomainTag.SYSTEM,
        EffectTag.READ_ONLY,
        AudienceTag.AGENT_SAFE,
        ScopeTag.HOST,
        ScopeTag.LOCAL,
    ],
)
def system__kill__by_port(context: ExecutionContext, port: int):
    from wexample_app.response.failure_response import FailureResponse
    from wexample_app.response.success_response import SuccessResponse
    from wexample_app.response.warning_response import WarningResponse

    proc = system_find_process_by_port(port)

    if not proc:
        return WarningResponse(
            kernel=context.kernel, message=f"No process found on port {port}"
        )

    try:
        proc.terminate()
        proc.wait(timeout=5)
        return SuccessResponse(
            kernel=context.kernel,
            message=f"Process {proc.pid} on port {port} terminated",
        )
    except psutil.TimeoutExpired:
        proc.kill()
        return SuccessResponse(
            kernel=context.kernel,
            message=f"Process {proc.pid} on port {port} killed (force)",
        )
    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
        return FailureResponse(
            kernel=context.kernel,
            message=f"Could not kill process on port {port}: {e}",
        )
