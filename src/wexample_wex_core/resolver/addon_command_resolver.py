from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from wexample_wex_core.resolver.abstract_command_resolver import AbstractCommandResolver

if TYPE_CHECKING:
    from wexample_wex_core.common.abstract_addon_manager import AbstractAddonManager
    from wexample_wex_core.common.command_address import CommandAddress
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

    def build_registry_data(self) -> RegistryResolverData:
        import importlib.util

        from wexample_wex_core.common.abstract_addon_manager import AbstractAddonManager
        from wexample_wex_core.common.command_address import CommandAddress
        from wexample_wex_core.common.command_method_wrapper import CommandMethodWrapper
        from wexample_wex_core.const.registries import RegistryAddonData, RegistryCommandData

        registry: RegistryResolverData = {}

        for addon in self.kernel.get_addons().values():
            assert isinstance(addon, AbstractAddonManager)

            addon_name = addon.get_snake_short_class_name()
            addon_data: RegistryAddonData = {}
            commands_base = addon.workdir.get_path() / "commands"

            if commands_base.exists():
                for group_dir in sorted(commands_base.iterdir()):
                    if not group_dir.is_dir() or group_dir.name.startswith("_"):
                        continue

                    for cmd_file in sorted(group_dir.iterdir()):
                        if cmd_file.suffix != ".py" or cmd_file.name.startswith("_"):
                            continue

                        address = CommandAddress.from_path(
                            path=cmd_file,
                            addon_name=addon_name,
                            commands_base=commands_base,
                        )
                        tests_base = addon.workdir.get_path() / "tests"
                        test_path = tests_base / address.to_relative_path()

                        # Load module to extract decorator metadata (description, aliases, attachments)
                        description: str | None = None
                        aliases: list[str] = []
                        attachments: dict[str, list] = {"before": [], "after": []}
                        sudo: bool = False
                        func_name = address.to_function_name()
                        spec = importlib.util.spec_from_file_location(func_name, cmd_file)
                        if spec and spec.loader:
                            mod = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(mod)  # type: ignore[union-attr]
                            wrapper = getattr(mod, func_name, None)
                            if isinstance(wrapper, CommandMethodWrapper):
                                description = wrapper.description
                                aliases = list(wrapper.aliases)
                                attachments = {
                                    pos: list(items)
                                    for pos, items in wrapper.attachments.items()
                                }
                                sudo = wrapper.sudo

                        addon_data[address.to_command_key()] = RegistryCommandData(
                            command=self.address_to_command(address),
                            path=str(cmd_file),
                            test=str(test_path) if test_path.exists() else None,
                            description=description,
                            alias=aliases,
                            attachments=attachments,
                            sudo=sudo,
                        )

            registry[addon_name] = addon_data

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
