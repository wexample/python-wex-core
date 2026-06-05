from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_cli.decorator.alias import alias
from wexample_cli.decorator.command import command
from wexample_cli.const.tags import AudienceTag, EffectTag, ScopeTag
from wexample_wex_core.addons.core.const.tags import DomainTag

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON

if TYPE_CHECKING:
    from wexample_cli.context.execution_context import ExecutionContext


@alias("version")
@command(
    type=COMMAND_TYPE_ADDON,
    description="Returns core version",
    tags=[
        DomainTag.CORE,
        DomainTag.PACKAGE,
        DomainTag.RELEASE,
        EffectTag.READ_ONLY,
        AudienceTag.AGENT_SAFE,
        ScopeTag.LOCAL,
        ScopeTag.NO_CONTEXT,
    ],
)
def core__version__get(context: ExecutionContext) -> str:
    return context.kernel.workdir.get_setup_version()
