from typing import Dict, Any

from wexample_wex_core.middleware.abstract_each_path_middleware import AbstractEachPathMiddleware


class EachDirectoryMiddleware(AbstractEachPathMiddleware):
    def _get_default_option(self) -> Dict[str, Any]:
        """Get the default directory option definition."""
        return {
            "name": "directory",
            "type": str,
            "required": True,
            "description": "Path to local directory"
        }
