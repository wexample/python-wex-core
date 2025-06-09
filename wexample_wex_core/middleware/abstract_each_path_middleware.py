from typing import Dict, Any, Optional

from wexample_wex_core.middleware.abstract_middleware import AbstractMiddleware, OptionDefinition


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
        """Get the default path option definition."""
        return {
            "name": "path",
            "type": str,
            "required": True,
            "description": "Path to local file or directory"
        }

    def get_path_option(self) -> Optional[OptionDefinition]:
        """Get the path option from the normalized options."""
        options = self._normalize_options()
        if options:
            return options[0]
        return None
