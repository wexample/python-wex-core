from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_cli.decorator.command import command

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON

if TYPE_CHECKING:
    from wexample_cli.context.execution_context import ExecutionContext


@command(type=COMMAND_TYPE_ADDON)
def core__info__show(context: ExecutionContext) -> PropertiesResponse:
    import platform

    from wexample_app.response.properties_response import PropertiesResponse

    registry = context.kernel.get_configuration_registry()

    return PropertiesResponse(
        kernel=context.kernel,
        title="General",
        properties={
            "Location": context.kernel.workdir.get_path(),
            "Environment": registry.env,
            "Arguments": context.kernel._sys_argv,
            "Python version": platform.python_version(),
        },
    )
