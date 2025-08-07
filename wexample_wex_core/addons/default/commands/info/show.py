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
            "Location": context.workdir.get_resolved(),
            "Environment": context.get_env_parameter(ENV_VAR_NAME_APP_ENV),
            "Arguments": context._sys_argv,
        }
    )

    context.io.properties(
        title="Resolvers",
        properties=context.get_resolvers()
    )

    context.io.properties(
        title="Runners",
        properties=context.get_runners()
    )
