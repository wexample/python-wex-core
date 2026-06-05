from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_cli.decorator.as_sudo import as_sudo
from wexample_cli.decorator.command import command
from wexample_cli.const.tags import AudienceTag, EffectTag, ScopeTag
from wexample_wex_core.addons.demo.const.tags import DomainTag

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON

if TYPE_CHECKING:
    from wexample_app.response.abstract_response import AbstractResponse
    from wexample_cli.context.execution_context import ExecutionContext


@as_sudo()
@command(type=COMMAND_TYPE_ADDON, description="Demo command that requires sudo",
    tags=[
        DomainTag.DEMO,
        EffectTag.READ_ONLY,
        AudienceTag.AGENT_SAFE,
        AudienceTag.DEV_TOOL,
        ScopeTag.NO_CONTEXT,
    ],
)
def demo__sudo__check(context: ExecutionContext) -> AbstractResponse:
    import os

    from wexample_app.response.dict_response import DictResponse

    return DictResponse(
        kernel=context.kernel,
        content={"user": os.getenv("USER", "unknown"), "uid": os.getuid()},
    )
