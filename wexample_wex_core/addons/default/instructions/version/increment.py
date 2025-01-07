from wexample_wex_addon_default.const.types import (UPGRADE_TYPE_MINOR)
from wexample_wex_addon_default.helpers.version import version_increment


def default__version__increment(
    kernel: "Kernel",
    version: str,
    type: str = UPGRADE_TYPE_MINOR,
    increment: int = 1,
    build: bool = False,
) -> str:
    return version_increment(
        version=version,
        type=type,
        increment=increment,
        build=build,
    )
