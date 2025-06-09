import os.path
from typing import TYPE_CHECKING, Dict, Any, List

from wexample_wex_core.exception.path_is_not_file_command_option_exception import PathIsNotFileCommandOptionException
from wexample_wex_core.middleware.abstract_each_path_middleware import AbstractEachPathMiddleware

if TYPE_CHECKING:
    from wexample_helpers.const.types import Kwargs
    from wexample_wex_core.common.command_request import CommandRequest
    from wexample_wex_core.common.command_method_wrapper import CommandMethodWrapper


class EachFileMiddleware(AbstractEachPathMiddleware):
    def _get_default_option(self) -> Dict[str, Any]:
        from wexample_helpers.const.globals import PATH_NAME_FILE

        """Get the default file option definition."""
        return {
            "name": PATH_NAME_FILE,
            "type": str,
            "required": True,
            "description": "Path to local file"
        }

    def validate_options(
            self,
            command_wrapper: "CommandMethodWrapper",
            request: "CommandRequest",
            function_kwargs: "Kwargs"
    ) -> bool:
        valid = super().validate_options(
            command_wrapper=command_wrapper,
            request=request,
            function_kwargs=function_kwargs,
        )

        # Do not search files in directory, so we check validity of curren given path.
        if valid and not self.expand_glob:
            option = self.get_first_option()
            file_path = function_kwargs[option.name]
            if not os.path.isfile(file_path):
                raise PathIsNotFileCommandOptionException(
                    option_name=option.name,
                    file_path=file_path
                )

            return True

        return valid
