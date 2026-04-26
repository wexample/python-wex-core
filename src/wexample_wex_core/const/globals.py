from __future__ import annotations

from pathlib import Path

from wexample_app.const.path import APP_DIR_NAME_TMP

# filestate: python-constant-sort
CORE_COMMAND_NAME: str = "wex"
CORE_DIR_NAME_KNOWLEDGE: Path = Path("knowledge")
CORE_DIR_NAME_LOGS: Path = Path("logs")
CORE_DIR_NAME_LOGS_ERRORS: Path = Path("errors")
CORE_DIR_NAME_TMP: Path = APP_DIR_NAME_TMP
CORE_FILE_NAME_APPS_REGISTRY: Path = Path("apps_registry.yml")
CORE_FILE_NAME_REGISTRY: Path = Path("registry.yml")

# filestate: python-constant-sort
COMMAND_SEPARATOR_ADDON: str = "::"
COMMAND_SEPARATOR_FUNCTION_PARTS: str = "__"
COMMAND_SEPARATOR_GROUP: str = "/"

# Command prefix characters
# filestate: python-constant-sort
COMMAND_CHAR_APP: str = "."
COMMAND_CHAR_SERVICE: str = "@"
COMMAND_CHAR_USER: str = "~"

# Command types
# filestate: python-constant-sort
COMMAND_TYPE_ADDON: str = "addon"
COMMAND_TYPE_APP: str = "app"
COMMAND_TYPE_SERVICE: str = "service"
COMMAND_TYPE_USER: str = "user"

# Command patterns
# filestate: python-constant-sort
COMMAND_PATTERN_ADDON: str = r"^(?:([a-zA-Z0-9-]+)::)?([a-zA-Z0-9-]+)/([a-zA-Z0-9-]+)$"
COMMAND_PATTERN_APP: str = r"^\.([a-zA-Z0-9-]+)/([a-zA-Z0-9-]+)$"
COMMAND_PATTERN_SERVICE: str = r"^@([a-zA-Z0-9-]+)::([a-zA-Z0-9-]+)/([a-zA-Z0-9-]+)$"
COMMAND_PATTERN_USER: str = r"^~([a-zA-Z0-9-]+)/([a-zA-Z0-9-]+)$"

COMMAND_PATTERNS: list[str] = [
    # filestate: python-iterable-sort
    COMMAND_PATTERN_ADDON,
    COMMAND_PATTERN_APP,
    COMMAND_PATTERN_SERVICE,
    COMMAND_PATTERN_USER,
]
