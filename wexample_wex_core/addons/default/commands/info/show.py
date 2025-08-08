from typing import TYPE_CHECKING

from wexample_wex_core.decorator.command import command

if TYPE_CHECKING:
    from wexample_wex_core.common.execution_context import ExecutionContext


@command()
def default__info__show(
        context: "ExecutionContext"
) -> None:
    from wexample_app.const.globals import ENV_VAR_NAME_APP_ENV

    context.io.properties(
        title="General",
        properties={
            "Location": context.kernel.workdir.get_resolved(),
            "Environment": context.kernel.get_env_parameter(ENV_VAR_NAME_APP_ENV),
            "Arguments": context.kernel._sys_argv,
        }
    )

    context.kernel.io.properties(
        title="Resolvers",
        properties=context.kernel.get_resolvers()
    )

    context.kernel.io.properties(
        title="Runners",
        properties=context.kernel.get_runners()
    )
