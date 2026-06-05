from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_cli.decorator.alias import alias
from wexample_cli.decorator.command import command
from wexample_cli.const.tags import AudienceTag, EffectTag, ScopeTag
from wexample_wex_core.addons.core.const.tags import DomainTag

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON

if TYPE_CHECKING:
    from wexample_app.response.abstract_response import AbstractResponse
    from wexample_cli.context.execution_context import ExecutionContext


@alias("hi")
@command(
    type=COMMAND_TYPE_ADDON,
    description="Return hi! Used to check if core vitals are working",
    tags=[
        DomainTag.CORE,
        DomainTag.DEMO,
        DomainTag.INTROSPECTION,
        EffectTag.READ_ONLY,
        AudienceTag.AGENT_SAFE,
        ScopeTag.LOCAL,
        ScopeTag.NO_CONTEXT,
    ],
)
def core__ping__hi(context: ExecutionContext) -> AbstractResponse:
    from wexample_app.response.default_response import DefaultResponse

    return DefaultResponse(kernel=context.kernel, content="hi!")
