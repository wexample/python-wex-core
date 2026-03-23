from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from wexample_wex_core.const.registries import RegistryResolverData
from wexample_wex_core.resolver.abstract_command_resolver import AbstractCommandResolver

if TYPE_CHECKING:
    from pathlib import Path

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

        from wexample_wex_core.const.globals import COMMAND_SEPARATOR_FUNCTION_PARTS

        return COMMAND_SEPARATOR_FUNCTION_PARTS.join(
            string_to_snake_case(part)
            for part in self.get_function_name_parts(request.match.groups())
        )

    def build_command_path(
        self, request: CommandRequest, extension: str
    ) -> Path | None:
        from wexample_helpers.helpers.string import string_to_snake_case

        match = request.match

        # Extract addon, group and command from match
        group = string_to_snake_case(match.group(2))
        command = string_to_snake_case(match.group(3))

        addon_manager = self.get_request_addon_manager(request)

        return (
            addon_manager.workdir.get_path()
            / "commands"
            / group
            / f"{command}.{extension}"
        )

    def build_registry_data(self) -> RegistryResolverData:
        import importlib.util

        from wexample_wex_core.common.abstract_addon_manager import AbstractAddonManager
        from wexample_wex_core.common.command_method_wrapper import CommandMethodWrapper
        from wexample_wex_core.const.registries import RegistryAddonData, RegistryCommandData

        registry: RegistryResolverData = {}

        for addon in self.kernel.get_addons().values():
            assert isinstance(addon, AbstractAddonManager)

            addon_name = addon.get_snake_short_class_name()
            addon_data: RegistryAddonData = {}
            commands_dir = addon.workdir.get_path() / "commands"

            if commands_dir.exists():
                for group_dir in sorted(commands_dir.iterdir()):
                    if not group_dir.is_dir() or group_dir.name.startswith("_"):
                        continue

                    for cmd_file in sorted(group_dir.iterdir()):
                        if cmd_file.suffix != ".py" or cmd_file.name.startswith("_"):
                            continue

                        group = group_dir.name
                        cmd = cmd_file.stem
                        command_key = f"{group}/{cmd}"
                        test_path = addon.workdir.get_path() / "tests" / group / f"{cmd}.py"

                        # Load module to extract decorator metadata (description, aliases)
                        description: str | None = None
                        aliases: list[str] = []
                        try:
                            func_name = f"{addon_name}__{group}__{cmd}"
                            spec = importlib.util.spec_from_file_location(func_name, cmd_file)
                            if spec and spec.loader:
                                mod = importlib.util.module_from_spec(spec)
                                spec.loader.exec_module(mod)  # type: ignore[union-attr]
                                wrapper = getattr(mod, func_name, None)
                                if isinstance(wrapper, CommandMethodWrapper):
                                    description = wrapper.description
                                    aliases = list(wrapper.aliases)
                        except Exception:
                            pass

                        addon_data[command_key] = RegistryCommandData(
                            command=f"{addon_name}::{command_key}",
                            path=str(cmd_file),
                            test=str(test_path) if test_path.exists() else None,
                            description=description,
                            alias=aliases,
                        )

            registry[addon_name] = addon_data

        return registry

    def supports(self, request: CommandRequest) -> object:
        match = self.build_match(request.name)

        if match:
            return match

        # Transparent alias resolution: if the input matches a registered alias,
        # redirect to the canonical command name before pattern matching.
        canonical = self._resolve_alias(request.name)
        if canonical:
            request.name = canonical
            return self.build_match(canonical)

        return None

    def _resolve_alias(self, name: str) -> str | None:
        try:
            registry = self.kernel.get_configuration_registry()
            for addon_data in registry.get_addon_commands().values():
                for cmd_data in addon_data.values():
                    if name in cmd_data.get("alias", []):
                        return cmd_data["command"]
        except Exception:
            pass
        return None

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
            # Get list of available addons for better error reporting
            available_addons = list(addon_registry.get_all().keys())
            raise AddonNotRegisteredException(
                addon_name=addon_name, available_addons=available_addons
            )

        return addon_registry.get(addon_name)
