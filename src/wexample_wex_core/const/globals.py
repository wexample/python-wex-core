from __future__ import annotations

CORE_COMMAND_NAME: str = "wex"
WORKDIR_SETUP_DIR: str = f".{CORE_COMMAND_NAME}"
CORE_FILE_NAME_REGISTRY: str = "registry.yml"
CORE_DIR_NAME_TMP: str = "tmp"

# Command types
# filestate: python-constant-sort
COMMAND_TYPE_ADDON: str = "addon"
COMMAND_TYPE_SERVICE: str = "service"

# Command patterns
# filestate: python-constant-sort
COMMAND_PATTERN_ADDON = r"^(?:([\w_-]+)::)?([\w_-]+)/([\w_-]+)$"
COMMAND_PATTERN_SERVICE = r"^@([\w_-]+)::([\w_-]+)/([\w_-]+)$"

COMMAND_SEPARATOR_FUNCTION_PARTS: str = "__"
