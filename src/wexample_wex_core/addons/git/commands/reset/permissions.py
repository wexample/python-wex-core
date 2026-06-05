from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_cli.decorator.command import command
from wexample_cli.const.tags import AudienceTag, EffectTag, ScopeTag
from wexample_wex_core.addons.git.const.tags import DomainTag

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON

if TYPE_CHECKING:
    from wexample_cli.context.execution_context import ExecutionContext


@command(type=COMMAND_TYPE_ADDON,
    tags=[
        DomainTag.GIT,
        EffectTag.SUBPROCESS_SPAWN,
        AudienceTag.AGENT_SAFE,
        ScopeTag.LOCAL,
        ScopeTag.PROJECT,
    ],
)
def git__reset__permissions(
    context: ExecutionContext,
) -> str:
    from wexample_helpers.helpers.shell import shell_run

    # Reset file permissions to match HEAD without changing content
    shell_run(
        "git diff --summary | grep 'mode change' | awk '{print $NF}' | xargs -r git checkout-index --force --",
        cwd=context.kernel._call_workdir.get_path(),
        shell=True,
        inherit_stdio=True,
    )
