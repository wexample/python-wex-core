from __future__ import annotations

from pathlib import Path

CORE_COMMAND_NAME: str = "wex"
WORKDIR_SETUP_DIR: Path = Path(f".{CORE_COMMAND_NAME}")

CORE_FILE_NAME_REGISTRY: Path = Path("registry.yml")
CORE_DIR_NAME_TMP: Path = Path("tmp")
CORE_DIR_NAME_KNOWLEDGE: Path = Path("knowledge")
# filestate: python-constant-sort
COMMAND_SEPARATOR_ADDON = "::"
COMMAND_SEPARATOR_FUNCTION_PARTS = "__"
COMMAND_SEPARATOR_GROUP = "/"

# Command types
COMMAND_TYPE_ADDON: str = "addon"
COMMAND_TYPE_SERVICE: str = "service"

# Command patterns
# filestate: python-constant-sort
COMMAND_PATTERN_ADDON = r"^(?:([\w_-]+)::)?([\w_-]+)/([\w_-]+)$"
COMMAND_PATTERN_SERVICE = r"^@([\w_-]+)::([\w_-]+)/([\w_-]+)$"

COMMAND_SEPARATOR_FUNCTION_PARTS: str = "__"
