from typing import Mapping, TypedDict, Optional

from wexample_helpers.const.types import StringsList, BasicInlineValue

# Core command types
CoreCommandArgsDict = Mapping[str, BasicInlineValue]
CoreCommandArgsList = StringsList

# Version types
UPGRADE_TYPE_MAJOR: str = "major"
UPGRADE_TYPE_INTERMEDIATE: str = "intermediate"
UPGRADE_TYPE_MINOR: str = "minor"
UPGRADE_TYPE_ALPHA: str = "alpha"
UPGRADE_TYPE_BETA: str = "beta"
UPGRADE_TYPE_DEV: str = "dev"
UPGRADE_TYPE_RC: str = "rc"
UPGRADE_TYPE_NIGHTLY: str = "nightly"
UPGRADE_TYPE_SNAPSHOT: str = "snapshot"

VERSION_PRE_BUILD_NUMBER: int = 0


class VersionDescriptor(TypedDict):
    major: Optional[int]
    intermediate: Optional[int]
    minor: Optional[int]
    pre_build_type: Optional[str]
    pre_build_number: Optional[int]
