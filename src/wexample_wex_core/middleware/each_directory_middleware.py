from __future__ import annotations

from typing import TYPE_CHECKING, Any

from wexample_wex_core.middleware.abstract_each_path_middleware import (
    AbstractEachPathMiddleware,
)

if TYPE_CHECKING:
    from wexample_helpers.const.types import Kwargs
    from wexample_wex_core.common.command_method_wrapper import CommandMethodWrapper
    from wexample_wex_core.common.command_request import CommandRequest


class EachDirectoryMiddleware(AbstractEachPathMiddleware):
    def validate_options(
        self,
        command_wrapper: CommandMethodWrapper,
        request: CommandRequest,
        function_kwargs: Kwargs,
    ) -> bool:
        from wexample_wex_core.exception.path_is_not_directory_command_option_exception import (
            PathIsNotDirectoryCommandOptionException,
        )

        if super().validate_options(
            command_wrapper=command_wrapper,
            request=request,
            function_kwargs=function_kwargs,
        ):
            option = self.get_first_option()
            directory_path = function_kwargs[option.name]
            if not os.path.isdir(directory_path):
                raise PathIsNotDirectoryCommandOptionException(
                    option_name=option.name, directory_path=directory_path
                )

            return True

        return False

    def _get_default_option(self) -> dict[str, Any]:
        """Get the default directory option definition."""
        from wexample_file.const.globals import PATH_NAME_DIRECTORY

        return {
            "name": PATH_NAME_DIRECTORY,
            "type": str,
            "required": True,
            "description": "Path to local directory",
        }

    def _should_process_item(self, request: CommandRequest, item_path: str) -> bool:
        return os.path.isdir(item_path)
