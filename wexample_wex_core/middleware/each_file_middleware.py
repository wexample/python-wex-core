from typing import Dict, Any

from wexample_wex_core.middleware.abstract_each_path_middleware import AbstractEachPathMiddleware


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
