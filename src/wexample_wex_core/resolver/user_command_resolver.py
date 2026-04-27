from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

from wexample_wex_core.resolver.abstract_command_resolver import AbstractCommandResolver

if TYPE_CHECKING:
    from wexample_wex_core.common.command_address import CommandAddress
    from wexample_wex_core.common.command_request import CommandRequest
    from wexample_wex_core.const.registries import RegistryResolverData

_USER_WEX_DIR = ".wex"
_COMMANDS_SUBDIR = "commands"


class UserCommandResolver(AbstractCommandResolver):
    """Resolves user-local commands: ``~group/name``.

    Commands live in ``~/.wex/commands/group/name.py`` or ``.yml``.
    """

    # ------------------------------------------------------------------
    # Command string format — ``~group/name`` instead of ``user::group/name``
    # ------------------------------------------------------------------
    @classmethod
    def address_to_command(cls, address: CommandAddress) -> str:
        from wexample_helpers.helpers.string import string_to_kebab_case

        from wexample_wex_core.const.globals import (
            COMMAND_CHAR_USER,
            COMMAND_SEPARATOR_GROUP,
        )

        return f"{COMMAND_CHAR_USER}{string_to_kebab_case(address.group)}{COMMAND_SEPARATOR_GROUP}{string_to_kebab_case(address.name)}"

    @classmethod
    def get_pattern(cls) -> str:
        from wexample_wex_core.const.globals import COMMAND_PATTERN_USER

        return COMMAND_PATTERN_USER

    @classmethod
    def get_type(cls) -> str:
        from wexample_wex_core.const.globals import COMMAND_TYPE_USER

        return COMMAND_TYPE_USER

    # ------------------------------------------------------------------
    # Registry
    # ------------------------------------------------------------------
    @classmethod
    def is_live(cls) -> bool:
        return True

    def autocomplete_suggest(self, cursor: int, search_split: list[str]) -> str | None:
        from wexample_wex_core.const.globals import COMMAND_CHAR_USER

        base = self.get_base_path()
        if not base:
            return None

        first = search_split[0] if search_split else ""

        if cursor == 0:
            # User commands are local — scan filesystem directly, not the registry
            commands_base = base / _COMMANDS_SUBDIR
            user_data = self._scan_commands_dir(commands_base, "user")
            user_cmds = sorted(cmd["command"] for cmd in user_data.values())

            if not user_cmds:
                return None

            if first == "":
                return f"\\{COMMAND_CHAR_USER}"
            if first.startswith(COMMAND_CHAR_USER):
                matches = [c for c in user_cmds if c.startswith(first)]
                return " ".join(matches) or None

        return None

    def build_command_function_name(self, request: CommandRequest) -> str | None:
        from wexample_helpers.helpers.string import string_to_snake_case

        from wexample_wex_core.common.command_address import CommandAddress

        address = CommandAddress(
            addon="user",
            group=string_to_snake_case(request.match.group(1)),
            name=string_to_snake_case(request.match.group(2)),
        )
        return address.to_function_name()

    def build_command_path(
        self, request: CommandRequest, extension: str
    ) -> Path | None:
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

    # ------------------------------------------------------------------
    # Command creation
    # ------------------------------------------------------------------
    def build_new_command_target(
        self, command: str, extension: str
    ) -> tuple[Path, dict] | None:
        match = self.build_match(command)
        if not match:
            return None

        group = match.group(1).replace("-", "_")
        name = match.group(2).replace("-", "_")
        target = (
            Path.home()
            / _USER_WEX_DIR
            / _COMMANDS_SUBDIR
            / group
            / f"{name}.{extension}"
        )
        return target, {"_type": "user", "group": group, "name": name}

    def build_registry_data(self) -> RegistryResolverData:
        base = self.get_base_path()
        if not base:
            return {"user": {}}

        commands_base = base / _COMMANDS_SUBDIR
        return {"user": self._scan_commands_dir(commands_base, "user")}

    # ------------------------------------------------------------------
    # Path resolution
    # ------------------------------------------------------------------
    def get_base_path(self) -> Path | None:
        path = Path.home() / _USER_WEX_DIR
        return path if path.is_dir() else None

    def supports(self, request: CommandRequest) -> object:
        match = self.build_match(request.name)
        if not match:
            return None

        base = self.get_base_path()
        if not base:
            return None

        # Add user commands dir to sys.path so imports work in user scripts
        commands_path = base / _COMMANDS_SUBDIR
        if commands_path.is_dir() and str(commands_path) not in sys.path:
            sys.path.append(str(commands_path))

        return match
