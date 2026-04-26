from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON
from wexample_wex_core.decorator.command import command
from wexample_wex_core.decorator.option import option

if TYPE_CHECKING:
    from wexample_wex_core.context.execution_context import ExecutionContext


@option(name="search", short_name="s", type=str, required=False, default="")
@option(name="cursor", short_name="c", type=int, required=False, default=0)
@command(
    type=COMMAND_TYPE_ADDON,
    description="Suggest autocomplete options for a partial wex command",
)
def core__autocomplete__suggest(
    context: ExecutionContext,
    search: str = "",
    cursor: int = 0,
) -> str:
    registry = context.kernel.get_configuration_registry()
    search_split = search.split(" ") if search.strip() else [""]

    if cursor > len(search_split):
        return ""

    first = search_split[0] if search_split else ""
    second = search_split[1] if len(search_split) > 1 else ""
    third = search_split[2] if len(search_split) > 2 else ""

    all_commands = list(registry.get_all_commands().keys())
    addon_cmds = [c for c in all_commands if "::" in c and not c.startswith("@")]
    service_cmds = [c for c in all_commands if c.startswith("@")]
    user_cmds = [c for c in all_commands if c.startswith("~")]

    suggestions: list[str] = []

    # --- Service commands: @service::group/command ---
    # bash may split "@service" as ["@", "service"] — handle both cases
    if first.startswith("@") or first == "@":
        # Normalize: extract service name and compute cursor offset for bash-split "@"
        if first == "@":
            service_name = second
            offset = 1  # bash split "@" as its own word
        else:
            service_name = first[1:]
            offset = 0

        effective_cursor = cursor - offset
        eff_second = search_split[1 + offset] if len(search_split) > 1 + offset else ""
        eff_third = search_split[2 + offset] if len(search_split) > 2 + offset else ""

        service_names = sorted(set(c[1:].split("::")[0] for c in service_cmds if "::" in c))

        if effective_cursor == 0:
            # Suggest @service:: names
            suggestions = [f"@{s}::" for s in service_names if s.startswith(service_name)]

        elif effective_cursor == 1:
            if eff_second == "::":
                # @service:: — suggest groups
                groups = sorted(set(
                    c.split("::")[1].split("/")[0]
                    for c in service_cmds
                    if c.startswith(f"@{service_name}::")
                ))
                suggestions = [f"{g}/" for g in groups]
            elif eff_second == ":":
                suggestions = ["::"]
            else:
                # Still typing service name
                suggestions = [f"@{s}::" for s in service_names if s.startswith(eff_second)]

        elif effective_cursor >= 2:
            # cursor=2: on "::"; cursor=3+: on group/command partial
            if eff_second == "::":
                search_service = f"@{service_name}::"
                suggestions = sorted([
                    c[len(search_service):]
                    for c in service_cmds
                    if c.startswith(search_service) and c[len(search_service):].startswith(eff_third)
                ])

    # --- User commands: ~group/command ---
    elif first.startswith("~"):
        suggestions = sorted(c for c in user_cmds if c.startswith(first))

        # When only "~" is typed, suggest the escaped char if no user commands exist
        if not suggestions and first == "~":
            suggestions = ["\\~"]

    # --- Addon commands: addon::group/command ---
    else:
        if cursor == 0:
            # Suggest addon names with "::" suffix
            addon_names = sorted(set(c.split("::")[0] for c in addon_cmds if "::" in c))
            suggestions = [f"{a}::" for a in addon_names if a.startswith(first)]

            # Suggest "@" and "\~" prefixes when search is empty
            if not first:
                if service_cmds:
                    suggestions.append("@")
                if user_cmds:
                    suggestions.append("\\~")

            # Also suggest aliases (short forms without addon prefix)
            for cmd_data in registry.get_all_commands().values():
                for alias in cmd_data.get("alias", []):
                    if (
                        alias.startswith(first)
                        and "::" not in alias
                        and not alias.startswith("@")
                        and not alias.startswith("~")
                    ):
                        suggestions.append(alias)

        elif cursor == 1:
            if second == "::":
                # Suggest groups for this addon
                groups = sorted(set(
                    c.split("::")[1].split("/")[0]
                    for c in addon_cmds
                    if "::" in c and c.split("::")[0] == first
                ))
                suggestions = [f"{g}/" for g in groups]
            elif second == ":":
                suggestions = ["::"]

        elif cursor == 2:
            # Suggest group/command for this addon filtered by partial
            suggestions = sorted([
                c.split("::")[1]
                for c in addon_cmds
                if "::" in c and c.split("::")[0] == first and c.split("::")[1].startswith(third)
            ])

        # cursor >= 3: argument completion not yet implemented

    return " ".join(suggestions)
