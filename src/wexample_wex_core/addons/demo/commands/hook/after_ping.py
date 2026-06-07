from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_cli.const.tags import AudienceTag, EffectTag, ScopeTag
from wexample_cli.decorator.command import command

from wexample_wex_core.addons.demo.commands.ping.pong import demo__ping__pong
from wexample_wex_core.addons.demo.const.tags import DomainTag
from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON
from wexample_wex_core.decorator.attach import ATTACH_POSITION_AFTER, attach

if TYPE_CHECKING:
    from wexample_cli.context.execution_context import ExecutionContext


@attach(position=ATTACH_POSITION_AFTER, command=demo__ping__pong)
@command(
    type=COMMAND_TYPE_ADDON,
    description="Demo after-hook for demo::ping/pong",
    tags=[
        DomainTag.DEMO,
        EffectTag.READ_ONLY,
        AudienceTag.AGENT_SAFE,
        AudienceTag.DEV_TOOL,
        ScopeTag.NO_CONTEXT,
    ],
)
def demo__hook__after_ping(context: ExecutionContext) -> str:
    context.kernel.io.log("@attach after demo::ping/pong — hook ran!")
    # Store on kernel so the test can observe the side-effect across module boundaries.
    context.kernel._test_after_ping_ran = True
    return "hook ran"
