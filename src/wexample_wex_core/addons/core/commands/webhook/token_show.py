from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_cli.decorator.command import command
from wexample_cli.decorator.option import option
from wexample_cli.const.tags import AudienceTag, EffectTag, ScopeTag
from wexample_wex_core.addons.core.const.tags import DomainTag

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON

if TYPE_CHECKING:
    from wexample_cli.context.execution_context import ExecutionContext

_VALID_TYPES = ("addon", "service")


@option(
    "type_name",
    type=str,
    required=True,
    description="Webhook type: addon or service",
)
@option(
    "command_name",
    type=str,
    required=True,
    description="Command whose token should be shown, e.g. 'app::info/show'",
)
@command(
    type=COMMAND_TYPE_ADDON,
    description="Show the webhook token for an addon or service command",
    tags=[
        DomainTag.CORE,
        DomainTag.HTTP,
        DomainTag.WEBHOOK,
        EffectTag.READ_ONLY,
        AudienceTag.AGENT_SAFE,
        ScopeTag.GLOBAL,
        ScopeTag.LOCAL,
    ],
)
def core__webhook__token_show(
    context: ExecutionContext,
    type_name: str,
    command_name: str,
):
    from wexample_app.response.failure_response import FailureResponse
    from wexample_app.response.warning_response import WarningResponse

    if type_name not in _VALID_TYPES:
        return FailureResponse(
            kernel=context.kernel,
            message=f"--type must be one of: {', '.join(_VALID_TYPES)}",
        )

    token = context.kernel.workdir.get_local_data_value(
        f"webhook_tokens_{type_name}", command_name
    )
    if not token:
        return WarningResponse(
            kernel=context.kernel, message=f"No token found for {command_name}."
        )

    return f"{command_name}:  @yellow{{{token}}}"
