from typing import Type, List, TYPE_CHECKING

from wexample_wex_core.middleware.abstract_middleware import AbstractMiddleware

if TYPE_CHECKING:
    from wexample_wex_core.common.command_option import CommandOption


class AbstractEachPathMiddleware(AbstractMiddleware):
    recursive: bool = False
    option_name: str = 'path'
    option_type: Type = str
    option_required: bool = True
    option_description: str = "Path to local file or directory"

    def build_options(self) -> List["CommandOption"]:
        from wexample_wex_core.common.command_option import CommandOption
        return [
            CommandOption(
                name=self.option_name,
                type=self.option_type,
                required=self.option_required,
                description=self.option_description,
            )
        ]

