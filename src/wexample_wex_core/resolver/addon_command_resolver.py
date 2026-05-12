from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from wexample_wex_core.resolver.abstract_command_resolver import AbstractCommandResolver

if TYPE_CHECKING:
    from wexample_wex_core.common.abstract_addon_manager import AbstractAddonManager
    from wexample_wex_core.common.command_request import CommandRequest
    from wexample_wex_core.const.registries import RegistryResolverData


class AddonCommandResolver(AbstractCommandResolver):
    @classmethod
    def get_pattern(cls) -> str:
        from wexample_wex_core.const.globals import COMMAND_PATTERN_ADDON

        return COMMAND_PATTERN_ADDON

    @classmethod
    def get_type(cls) -> str:
        from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON

        return COMMAND_TYPE_ADDON

    def autocomplete_suggest(self, cursor: int, search_split: list[str]) -> str | None:
        from wexample_wex_core.const.globals import COMMAND_SEPARATOR_ADDON

        registry = self.kernel.get_configuration_registry()
        addon_data = registry.get_addon_commands()
        # addon_data: {addon_name: {cmd_key: {command: "addon::group/cmd", ...}}}

        all_addon_cmds = [
            cmd["command"] for addon in addon_data.values() for cmd in addon.values()
        ]

        first = search_split[0] if search_split else ""
        second = search_split[1] if len(search_split) > 1 else ""
        third = search_split[2] if len(search_split) > 2 else ""

        if cursor == 0:
            addon_names = sorted(
                {c.split("::")[0] for c in all_addon_cmds if "::" in c}
            )
            addon_name_matches = [a for a in addon_names if a.startswith(first)]
            if len(addon_name_matches) == 1:
                suggestions = [addon_name_matches[0] + COMMAND_SEPARATOR_ADDON]
            else:
                suggestions = addon_name_matches
            # Aliases (short forms without addon prefix)
            for cmd in addon_data.values():
                for cmd_data in cmd.values():
                    for alias in cmd_data.get("alias", []):
                        if alias.startswith(first) and "::" not in alias:
                            suggestions.append(alias)
            # Unqualified commands: group/name without addon:: prefix
            if "/" in first and "::" not in first:
                unqualified = sorted(
                    {
                        c.split("::")[1]
                        for c in all_addon_cmds
                        if "::" in c and c.split("::")[1].startswith(first)
                    }
                )
                suggestions.extend(unqualified)
            return " ".join(suggestions) if suggestions else None

        elif cursor == 1:
            if second == COMMAND_SEPARATOR_ADDON:
                groups = sorted(
                    {
                        c.split("::")[1].split("/")[0]
                        for c in all_addon_cmds
                        if "::" in c and c.split("::")[0] == first
                    }
                )
                return " ".join(f"{g}/" for g in groups) or None
            elif second == ":":
                return ":"

        elif cursor == 2:
            matches = sorted(
                [
                    c.split("::")[1]
                    for c in all_addon_cmds
                    if "::" in c
                    and c.split("::")[0] == first
                    and c.split("::")[1].startswith(third)
                ]
            )
            return " ".join(matches) or None

        return None

    def build_command_function_name(self, request: CommandRequest) -> str | None:
        from wexample_helpers.helpers.string import string_to_snake_case

        from wexample_wex_core.common.command_address import CommandAddress

        address = CommandAddress(
            addon=string_to_snake_case(request.match.group(1)),
            group=string_to_snake_case(request.match.group(2)),
            name=string_to_snake_case(request.match.group(3)),
        )
        return address.to_function_name()

    def build_command_path(
        self, request: CommandRequest, extension: str
    ) -> Path | None:
        from wexample_helpers.helpers.string import string_to_snake_case

        from wexample_wex_core.common.command_address import CommandAddress

        address = CommandAddress(
            addon=string_to_snake_case(request.match.group(1)),
            group=string_to_snake_case(request.match.group(2)),
            name=string_to_snake_case(request.match.group(3)),
        )
        addon_manager = self.get_request_addon_manager(request)
        commands_base = addon_manager.workdir.get_path() / "commands"

        return commands_base / address.to_relative_path(extension=extension)

    def build_new_command_target(
        self, command: str, extension: str
    ) -> tuple[Path, dict] | None:
        from wexample_helpers.helpers.string import string_to_snake_case

        match = self.build_match(command)
        if not match or not match.group(1):
            return None  # addon name is required for creation

        addon_name = string_to_snake_case(match.group(1))
        group = string_to_snake_case(match.group(2))
        name = string_to_snake_case(match.group(3))

        addon = self.kernel.get_addons().get(addon_name)
        if not addon:
            return None

        target = addon.workdir.get_path() / "commands" / group / f"{name}.{extension}"
        return target, {
            "_type": "addon",
            "addon": addon_name,
            "group": group,
            "name": name,
        }

    def build_registry_data(self) -> RegistryResolverData:
        from wexample_wex_core.common.abstract_addon_manager import AbstractAddonManager

        registry: RegistryResolverData = {}

        for addon in self.kernel.get_addons().values():
            assert isinstance(addon, AbstractAddonManager)

            addon_name = addon.get_snake_short_class_name()
            commands_base = addon.workdir.get_path() / "commands"
            registry[addon_name] = self._scan_commands_dir(commands_base, addon_name)

        return registry

    def get_request_addon_manager(
        self, request: CommandRequest
    ) -> AbstractAddonManager:
        from wexample_helpers.helpers.string import string_to_snake_case

        from wexample_wex_core.exception.addon_not_registered_exception import (
            AddonNotRegisteredException,
        )

        match = request.match
        addon_name = string_to_snake_case(match.group(1))
        addon_registry = self.kernel.get_registry("addon")

        if not addon_registry.has(addon_name):
            available_addons = list(addon_registry.get_all().keys())
            raise AddonNotRegisteredException(
                addon_name=addon_name, available_addons=available_addons
            )

        return addon_registry.get(addon_name)
