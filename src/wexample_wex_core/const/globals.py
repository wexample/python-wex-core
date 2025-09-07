from __future__ import annotations

CORE_COMMAND_NAME = "wex"
WORKDIR_SETUP_DIR = f".{CORE_COMMAND_NAME}"

# Command types
# filestate: python-constant-sort
COMMAND_TYPE_ADDON = "addon"
COMMAND_TYPE_SERVICE = "service"

# Command patterns
# filestate: python-constant-sort
COMMAND_PATTERN_ADDON = r"^(?:([\w_-]+)::)?([\w_-]+)/([\w_-]+)$"
COMMAND_PATTERN_SERVICE = r"^@([\w_-]+)::([\w_-]+)/([\w_-]+)$"

COMMAND_SEPARATOR_FUNCTION_PARTS = "__"
