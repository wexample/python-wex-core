from pathlib import Path
from typing import Optional, TYPE_CHECKING

from wexample_app.resolver.abstract_command_resolver import AbstractCommandResolver
from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON, COMMAND_PATTERN_ADDON
from wexample_helpers.const.globals import FILE_EXTENSION_PYTHON
from wexample_helpers.helpers.string import string_to_snake_case

if TYPE_CHECKING:
    from wexample_app.common.command_request import CommandRequest


class AddonCommandResolver(AbstractCommandResolver):
    @classmethod
    def get_pattern(cls) -> str:
        return COMMAND_PATTERN_ADDON

    @classmethod
    def get_type(cls) -> str:
        return COMMAND_TYPE_ADDON

    def build_command_path(self, request: "CommandRequest") -> Optional[str]:
        match = request.match

        # Extract addon, group and command from match
        addon = string_to_snake_case(match.group(1))
        group = string_to_snake_case(match.group(2))
        command = string_to_snake_case(match.group(3))

        # Build path: addons/[addon]/instructions/[group]/[command].py
        return str(Path(self.kernel.workdir.get_resolved()) / "addons" / addon / "instructions" / group / f"{command}.{FILE_EXTENSION_PYTHON}")

    def build_command_function_name(self, request: "CommandRequest") -> Optional[str]:
        # TODO: Convert command path to method name
        # Example: default::info/show -> default__info__show
        return None
