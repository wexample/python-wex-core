from typing import TYPE_CHECKING, Dict, Any, Optional

from wexample_wex_core.middleware.abstract_middleware import AbstractMiddleware

if TYPE_CHECKING:
    from wexample_helpers.const.types import Kwargs
    from wexample_wex_core.common.command_request import CommandRequest
    from wexample_wex_core.common.command_method_wrapper import CommandMethodWrapper


class AbstractEachPathMiddleware(AbstractMiddleware):
    recursive: bool = False
    should_exist: bool = False
    expand_glob: bool = False

    def __init__(self, **kwargs):
        # Set default option if none provided
        if 'option' not in kwargs or not kwargs['option']:
            kwargs['option'] = self._get_default_option()

        kwargs['options'] = [
            kwargs['option']
        ]

        super().__init__(**kwargs)

    def _get_option_file_path(self, function_kwargs: "Kwargs") -> Optional[str]:
        option = self.get_first_option()
        return function_kwargs[option.name]

    def _get_default_option(self) -> Dict[str, Any]:
        from wexample_helpers.const.globals import PATH_NAME_PATH
        """Get the default path option definition."""
        return {
            "name": PATH_NAME_PATH,
            "type": str,
            "required": True,
            "description": "Path to local file or directory"
        }

    def validate_options(
            self,
            command_wrapper: "CommandMethodWrapper",
            request: "CommandRequest",
            function_kwargs: "Kwargs"
    ) -> bool:
        if self.should_exist:
            import os.path
            from wexample_wex_core.exception.path_not_found_command_option_exception import \
                PathNotFoundCommandOptionException

            option = self.get_first_option()
            if option and option.name in function_kwargs:
                file_path = function_kwargs[option.name]
                if not os.path.exists(file_path):
                    raise PathNotFoundCommandOptionException(
                        option_name=option.name,
                        file_path=file_path
                    )

        return True
