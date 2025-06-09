from typing import Dict, Any

from wexample_wex_core.middleware.abstract_each_path_middleware import AbstractEachPathMiddleware


class EachFileMiddleware(AbstractEachPathMiddleware):
    def _get_default_option(self) -> Dict[str, Any]:
        """Get the default file option definition."""
        return {
            "name": "file",
            "type": str,
            "required": True,
            "description": "Path to local file"
        }
