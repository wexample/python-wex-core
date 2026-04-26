from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from wexample_wex_core.resolver.abstract_command_resolver import AbstractCommandResolver

if TYPE_CHECKING:
    from wexample_wex_core.common.command_address import CommandAddress
    from wexample_wex_core.common.command_request import CommandRequest
    from wexample_wex_core.const.registries import RegistryResolverData

_SERVICES_SUBDIR = "services"
_COMMANDS_SUBDIR = "commands"


class ServiceCommandResolver(AbstractCommandResolver):
    """Resolves commands scoped to a named service: ``@service::group/command``."""

    def autocomplete_suggest(self, cursor: int, search_split: list[str]) -> str | None:
        from wexample_wex_core.const.globals import (
            COMMAND_CHAR_SERVICE,
            COMMAND_SEPARATOR_ADDON,
        )

        service_cmds = list(
            self.kernel.get_configuration_registry()
            .get_all_commands()
            .keys()
        )
        service_cmds = [c for c in service_cmds if c.startswith(COMMAND_CHAR_SERVICE)]

        if not service_cmds:
            return None

        first = search_split[0] if search_split else ""

        # Suggest "@" when search is empty
        if cursor == 0 and first == "":
            return COMMAND_CHAR_SERVICE

        # All further suggestions require search to start with "@"
        if not first.startswith(COMMAND_CHAR_SERVICE):
            return None

        if cursor <= 1:
            # Suggest full @service:: names (or filtered by what follows "@")
            typed = "".join(search_split[: cursor + 1])
            matches = [c for c in service_cmds if c.startswith(typed)]
            # Return up to the "::" separator, de-duplicated
            suggestions = sorted(set(
                c[: c.index(COMMAND_SEPARATOR_ADDON) + len(COMMAND_SEPARATOR_ADDON)]
                for c in matches
                if COMMAND_SEPARATOR_ADDON in c
            ))
            return " ".join(suggestions) or None

        elif cursor == 2 or cursor == 3:
            if len(search_split) > 2 and search_split[2] == COMMAND_SEPARATOR_ADDON:
                search_service = "".join(search_split[:3])  # "@service::"
                typed = "".join(search_split)
                matches = [
                    c[len(search_service):]
                    for c in service_cmds
                    if c.startswith(typed)
                ]
                return " ".join(sorted(matches)) or None
            elif cursor == 2 and search_split[2] == ":":
                return COMMAND_SEPARATOR_ADDON

        return None

    @classmethod
    def address_to_command(cls, address: CommandAddress) -> str:
        from wexample_wex_core.const.globals import COMMAND_CHAR_SERVICE

        return f"{COMMAND_CHAR_SERVICE}{super().address_to_command(address)}"

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

    def build_command_path(
        self, request: CommandRequest, extension: str
    ) -> Path | None:
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

    def build_registry_data(self) -> RegistryResolverData:
        from wexample_wex_core.common.abstract_addon_manager import AbstractAddonManager

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
                addon_data = self._scan_commands_dir(commands_base, service_name)

                if service_name not in registry:
                    registry[service_name] = addon_data
                else:
                    registry[service_name].update(addon_data)

        return registry

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
