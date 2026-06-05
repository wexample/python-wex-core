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
@command(
    type=COMMAND_TYPE_ADDON,
    description="List all webhook tokens for addon or service commands",
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
def core__webhook__token_list(
    context: ExecutionContext,
    type_name: str,
):
    from wexample_app.response.failure_response import FailureResponse
    from wexample_app.response.table_response import TableResponse

    if type_name not in _VALID_TYPES:
        return FailureResponse(
            kernel=context.kernel,
            message=f"--type must be one of: {', '.join(_VALID_TYPES)}",
        )

    tokens: dict = context.kernel.workdir.get_local_data(f"webhook_tokens_{type_name}")

    if not tokens:
        return f"No webhook tokens registered for {type_name} commands."

    rows = [
        [cmd, f"@yellow{{{token[:8]}}}..."] for cmd, token in sorted(tokens.items())
    ]

    return TableResponse(
        kernel=context.kernel,
        content=rows,
        headers=["Command", "Token (prefix)"],
    )
