from typing import Optional, TYPE_CHECKING

from wexample_app.resolver.abstract_command_resolver import AbstractCommandResolver
from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON, COMMAND_PATTERN_ADDON

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
        # TODO: Implement path building based on addon name and command path
        # Example: addons/default/instructions/info/show.py
        return None

    def build_command_function_name(self, request: "CommandRequest") -> Optional[str]:
        # TODO: Convert command path to method name
        # Example: default::info/show -> default__info__show
        return None
