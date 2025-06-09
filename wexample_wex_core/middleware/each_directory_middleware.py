from typing import Dict, Any

from wexample_wex_core.middleware.abstract_each_path_middleware import AbstractEachPathMiddleware


class EachDirectoryMiddleware(AbstractEachPathMiddleware):
    def _get_default_option(self) -> Dict[str, Any]:
        from wexample_helpers.const.globals import PATH_NAME_DIRECTORY

        """Get the default directory option definition."""
        return {
            "name": PATH_NAME_DIRECTORY,
            "type": str,
            "required": True,
            "description": "Path to local directory"
        }
