from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_cli.decorator.command import command
from wexample_cli.decorator.option import option
from wexample_cli.const.tags import AudienceTag, EffectTag, ScopeTag
from wexample_wex_core.addons.core.const.tags import DomainTag

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON

if TYPE_CHECKING:
    from wexample_cli.context.execution_context import ExecutionContext


@option(name="search", short_name="s", type=str, required=False, default="")
@option(name="cursor", short_name="c", type=int, required=False, default=0)
@command(
    type=COMMAND_TYPE_ADDON,
    description="Suggest autocomplete options for a partial wex command",
    tags=[
        DomainTag.CORE,
        DomainTag.INTROSPECTION,
        EffectTag.READ_ONLY,
        AudienceTag.AGENT_SAFE,
        ScopeTag.LOCAL,
        ScopeTag.NO_CONTEXT,
    ],
)
def core__autocomplete__suggest(
    context: ExecutionContext,
    search: str = "",
    cursor: int = 0,
) -> str:
    search_split = search.split(" ") if search.strip() else [""]

    if cursor > len(search_split):
        return ""

    suggestions = ""
    for resolver in context.kernel.get_resolvers().values():
        result = resolver.autocomplete_suggest(cursor, search_split)
        if result:
            suggestions += " " + result

    return suggestions.strip()
