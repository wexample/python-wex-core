from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_cli.const.tags import AudienceTag, EffectTag, ScopeTag
from wexample_cli.decorator.command import command

from wexample_wex_core.addons.demo.const.tags import DomainTag
from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON

if TYPE_CHECKING:
    from wexample_app.response.abstract_response import AbstractResponse
    from wexample_cli.context.execution_context import ExecutionContext


@command(
    type=COMMAND_TYPE_ADDON,
    tags=[
        DomainTag.DEMO,
        EffectTag.READ_ONLY,
        AudienceTag.AGENT_SAFE,
        AudienceTag.DEV_TOOL,
        ScopeTag.NO_CONTEXT,
    ],
)
def demo__demo__demo(context: ExecutionContext) -> AbstractResponse:
    from wexample_app.response.str_response import StrResponse

    return StrResponse(kernel=context.kernel, content="demo")
