from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from wexample_wex_core.resolver.abstract_command_resolver import AbstractCommandResolver

if TYPE_CHECKING:
    from wexample_wex_core.common.command_request import CommandRequest
    from wexample_wex_core.const.registries import RegistryResolverData

_SERVICES_SUBDIR = "services"
_COMMANDS_SUBDIR = "commands"


class ServiceCommandResolver(AbstractCommandResolver):
    """Resolves commands scoped to a named service: ``@service::group/command``."""

    @classmethod
    def get_pattern(cls) -> str:
        from wexample_wex_core.const.globals import COMMAND_PATTERN_SERVICE

        return COMMAND_PATTERN_SERVICE

    @classmethod
    def get_type(cls) -> str:
        from wexample_wex_core.const.globals import COMMAND_TYPE_SERVICE

        return COMMAND_TYPE_SERVICE

    def build_command_function_name(self, request: CommandRequest) -> str | None:
        from wexample_helpers.helpers.string import string_to_snake_case

        from wexample_wex_core.common.command_address import CommandAddress

        address = CommandAddress(
            addon=string_to_snake_case(request.match.group(1)),
            group=string_to_snake_case(request.match.group(2)),
            name=string_to_snake_case(request.match.group(3)),
        )
        return address.to_function_name()

    def build_command_path(self, request: CommandRequest, extension: str) -> Path | None:
        from wexample_helpers.helpers.string import string_to_snake_case

        from wexample_wex_core.common.command_address import CommandAddress

        service_name = string_to_snake_case(request.match.group(1))
        service_dir = self._find_service_dir(service_name)
        if not service_dir:
            return None

        address = CommandAddress(
            addon=service_name,
            group=string_to_snake_case(request.match.group(2)),
            name=string_to_snake_case(request.match.group(3)),
        )
        return service_dir / _COMMANDS_SUBDIR / address.to_relative_path(extension)

    def _find_service_dir(self, service_name: str) -> Path | None:
        """Scan all addon directories for a matching service."""
        from wexample_wex_core.common.abstract_addon_manager import AbstractAddonManager

        for addon in self.kernel.get_addons().values():
            assert isinstance(addon, AbstractAddonManager)
            services_base = addon.workdir.get_path() / _SERVICES_SUBDIR
            if not services_base.is_dir():
                continue
            service_dir = services_base / service_name
            if service_dir.is_dir():
                return service_dir

        return None

    def build_registry_data(self) -> RegistryResolverData:
        import importlib.util

        from wexample_wex_core.common.abstract_addon_manager import AbstractAddonManager
        from wexample_wex_core.common.command_address import CommandAddress
        from wexample_wex_core.common.command_method_wrapper import CommandMethodWrapper
        from wexample_wex_core.const.registries import RegistryAddonData, RegistryCommandData

        registry: RegistryResolverData = {}

        for addon in self.kernel.get_addons().values():
            assert isinstance(addon, AbstractAddonManager)

            services_base = addon.workdir.get_path() / _SERVICES_SUBDIR
            if not services_base.is_dir():
                continue

            for service_dir in sorted(services_base.iterdir()):
                if not service_dir.is_dir() or service_dir.name.startswith("_"):
                    continue

                service_name = service_dir.name
                commands_base = service_dir / _COMMANDS_SUBDIR
                addon_data: RegistryAddonData = {}

                if commands_base.is_dir():
                    for group_dir in sorted(commands_base.iterdir()):
                        if not group_dir.is_dir() or group_dir.name.startswith("_"):
                            continue

                        for cmd_file in sorted(group_dir.iterdir()):
                            if cmd_file.suffix != ".py" or cmd_file.name.startswith("_"):
                                continue

                            address = CommandAddress.from_path(
                                path=cmd_file,
                                addon_name=service_name,
                                commands_base=commands_base,
                            )

                            description: str | None = None
                            aliases: list[str] = []
                            func_name = address.to_function_name()
                            spec = importlib.util.spec_from_file_location(func_name, cmd_file)
                            if spec and spec.loader:
                                mod = importlib.util.module_from_spec(spec)
                                spec.loader.exec_module(mod)  # type: ignore[union-attr]
                                wrapper = getattr(mod, func_name, None)
                                if isinstance(wrapper, CommandMethodWrapper):
                                    description = wrapper.description
                                    aliases = list(wrapper.aliases)

                            addon_data[address.to_command_key()] = RegistryCommandData(
                                command=f"@{address.to_command()}",
                                path=str(cmd_file),
                                test=None,
                                description=description,
                                alias=aliases,
                            )

                if service_name not in registry:
                    registry[service_name] = addon_data
                else:
                    registry[service_name].update(addon_data)

        return registry
