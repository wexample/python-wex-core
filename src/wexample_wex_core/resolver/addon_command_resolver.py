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
