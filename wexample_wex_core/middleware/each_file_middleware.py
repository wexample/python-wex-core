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
            file_path = self._get_option_file_path(function_kwargs=function_kwargs)
            if not os.path.isfile(file_path):
                option = self.get_first_option()
                raise PathIsNotFileCommandOptionException(
                    option_name=option.name,
                    file_path=file_path
                )

            return True

        return valid

    def build_execution_passes(
            self,
            command_wrapper: "CommandMethodWrapper",
            request: "CommandRequest",
            function_kwargs: "Kwargs"
    ) -> List["Kwargs"]:
        # If glob expansion is enabled and the path is a directory,
        # create an execution for each file in that directory
        if self.expand_glob:
            file_path = self._get_option_file_path(function_kwargs=function_kwargs)
            
            # If the path is a directory, process each file it contains
            if os.path.isdir(file_path):
                passes = []
                option = self.get_first_option()
                
                # Iterate through all directory items
                for item in os.listdir(file_path):
                    item_path = os.path.join(file_path, item)
                    
                    # Only process files (not subdirectories)
                    if os.path.isfile(item_path):
                        # Create a copy of arguments for each file
                        kwargs_copy = function_kwargs.copy()
                        kwargs_copy[option.name] = item_path
                        passes.append(kwargs_copy)
                        
                return passes
            
            # If the path is not a directory, continue normally
            # (validation will happen in validate_options)
            
        # If expand_glob is not enabled, use default behavior
        return super().build_execution_passes(
            command_wrapper=command_wrapper,
            request=request,
            function_kwargs=function_kwargs
        )
