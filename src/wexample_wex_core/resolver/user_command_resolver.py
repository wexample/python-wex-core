from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

from wexample_wex_core.resolver.abstract_command_resolver import AbstractCommandResolver

if TYPE_CHECKING:
    from wexample_wex_core.common.command_request import CommandRequest
    from wexample_wex_core.const.registries import RegistryResolverData

# User wex data lives at ~/.wex
_USER_WEX_DIR_NAME = ".wex"
_COMMANDS_SUBDIR = "commands"


class UserCommandResolver(AbstractCommandResolver):
    """Resolves commands local to the user: ``~group/command``."""

    @classmethod
    def get_pattern(cls) -> str:
        from wexample_wex_core.const.globals import COMMAND_PATTERN_USER

        return COMMAND_PATTERN_USER

    @classmethod
    def get_type(cls) -> str:
        from wexample_wex_core.const.globals import COMMAND_TYPE_USER

        return COMMAND_TYPE_USER

    def get_base_path(self) -> Path | None:
        """Return ``~/.wex`` if it exists, else None."""
        path = Path.home() / _USER_WEX_DIR_NAME
        return path if path.is_dir() else None

    def build_command_function_name(self, request: CommandRequest) -> str | None:
        from wexample_helpers.helpers.string import string_to_snake_case

        from wexample_wex_core.common.command_address import CommandAddress

        address = CommandAddress(
            addon="user",
            group=string_to_snake_case(request.match.group(1)),
            name=string_to_snake_case(request.match.group(2)),
        )
        return address.to_function_name()

    def build_command_path(self, request: CommandRequest, extension: str) -> Path | None:
        from wexample_helpers.helpers.string import string_to_snake_case

        from wexample_wex_core.common.command_address import CommandAddress

        base = self.get_base_path()
        if not base:
            return None

        address = CommandAddress(
            addon="user",
            group=string_to_snake_case(request.match.group(1)),
            name=string_to_snake_case(request.match.group(2)),
        )
        return base / _COMMANDS_SUBDIR / address.to_relative_path(extension)

    def supports(self, request: CommandRequest) -> object:
        match = self.build_match(request.name)
        if not match:
            return None

        # Only resolve if the user commands directory actually exists.
        if not self.get_base_path():
            return None

        # Add user command dir to sys.path so imports work in user scripts.
        commands_path = self.get_base_path() / _COMMANDS_SUBDIR
        if commands_path.is_dir() and str(commands_path) not in sys.path:
            sys.path.append(str(commands_path))

        return match

    def build_registry_data(self) -> RegistryResolverData:
        import importlib.util

        from wexample_wex_core.common.command_address import CommandAddress
        from wexample_wex_core.common.command_method_wrapper import CommandMethodWrapper
        from wexample_wex_core.const.registries import RegistryAddonData, RegistryCommandData

        base = self.get_base_path()
        if not base:
            return {}

        commands_base = base / _COMMANDS_SUBDIR
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
                        addon_name="user",
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
                        command=self.address_to_command(address),
                        path=str(cmd_file),
                        test=None,
                        description=description,
                        alias=aliases,
                    )

        return {"user": addon_data}
