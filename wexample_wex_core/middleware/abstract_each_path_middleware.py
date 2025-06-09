from typing import Dict, Any

from wexample_wex_core.middleware.abstract_middleware import AbstractMiddleware


class AbstractEachPathMiddleware(AbstractMiddleware):
    recursive: bool = False

    def __init__(self, **kwargs):
        # Set default option if none provided
        if 'option' not in kwargs or not kwargs['option']:
            kwargs['option'] = self._get_default_option()

        super().__init__(**kwargs)

        self.options = [
            kwargs['option']
        ]

    def _get_default_option(self) -> Dict[str, Any]:
        from wexample_helpers.const.globals import PATH_NAME_PATH
        """Get the default path option definition."""
        return {
            "name": PATH_NAME_PATH,
            "type": str,
            "required": True,
            "description": "Path to local file or directory"
        }
