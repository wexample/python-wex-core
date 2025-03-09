from pathlib import Path
from typing import Optional, TYPE_CHECKING, cast

from wexample_app.resolver.abstract_command_resolver import AbstractCommandResolver
from wexample_helpers.const.globals import FILE_EXTENSION_PYTHON
from wexample_helpers.helpers.string import string_to_snake_case
from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON, COMMAND_PATTERN_ADDON, COMMAND_SEPARATOR_FUNCTION_PARTS

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
        from wexample_wex_core.common.abstract_addon_manager import AbstractAddonManager

        match = request.match

        # Extract addon, group and command from match
        addon = string_to_snake_case(match.group(1))
        group = string_to_snake_case(match.group(2))
        command = string_to_snake_case(match.group(3))

        addon_manager = cast(AbstractAddonManager, self.kernel.get_registry('addon').get(addon))

        return str(
            Path(addon_manager.workdir.get_resolved())
            / "instructions"
            / group
            / f"{command}.{FILE_EXTENSION_PYTHON}"
        )

    def build_command_function_name(self, request: "CommandRequest") -> Optional[str]:
        return string_to_snake_case(
            COMMAND_SEPARATOR_FUNCTION_PARTS.join(self.get_function_name_parts(
                request.match.groups()
            ))
        )
