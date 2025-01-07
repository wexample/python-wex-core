import re
from typing import Optional

from wexample_wex_addon_default.const.types import VersionDescriptor, UPGRADE_TYPE_MINOR, UPGRADE_TYPE_MAJOR, \
    UPGRADE_TYPE_INTERMEDIATE, UPGRADE_TYPE_ALPHA, UPGRADE_TYPE_BETA, UPGRADE_TYPE_DEV, UPGRADE_TYPE_RC, \
    UPGRADE_TYPE_NIGHTLY, UPGRADE_TYPE_SNAPSHOT
from wexample_helpers.const.types import StringsList


def is_greater_than(
    first: VersionDescriptor, second: VersionDescriptor, true_if_equal: bool = False
) -> bool:
    keys_to_check: StringsList = [
        "major",
        "intermediate",
        "minor",
        "pre_build_type",
        "pre_build_number",
    ]

    for key in keys_to_check:
        first_value = first.get(key, None)
        second_value = second.get(key, None)

        if first_value is not None and second_value is None:
            return False
        elif first_value is None and second_value is not None:
            return True

        if first_value is not None and second_value is not None:
            assert isinstance(first_value, int)
            assert isinstance(second_value, int)
            if first_value < second_value:
                return False
            elif first_value > second_value:
                return True

    return true_if_equal


def version_join(version: VersionDescriptor, add_build: bool = False) -> str:
    output = f"{version['major']}.{version['intermediate']}.{version['minor']}"

    # Build version string
    if version["pre_build_type"]:
        output += f'-{version["pre_build_type"]}.{version["pre_build_number"]}'

    if add_build:
        import datetime

        output += f"+build." + datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    return output


def version_parse(version: str) -> VersionDescriptor | None:
    pre_build_number: Optional[int] = None
    pre_build_type: Optional[str] = None

    try:
        # Handle 1.0.0-beta.1+build.1234
        if "-" in version:
            base_version, pre_build = version.split("-")

            if "." in pre_build:
                pre_build_parts = pre_build.split(".")
                pre_build_type = pre_build_parts[0]

                # pre_build_number can be : 1+build.1234
                if "+" in pre_build_parts[1]:
                    pre_build_number_str, build_metadata = pre_build_parts[1].split("+")
                    pre_build_number = (
                        int(pre_build_number_str) if pre_build_number_str else None
                    )
                else:
                    pre_build_number = (
                        int(pre_build_parts[1]) if pre_build_parts[1] else None
                    )

        match = re.match(r"(\d+)?\.?(\d+)?\.?(\d+)?([-.+].*)?", version)
        major = intermediate = minor = None

        if match:
            major, intermediate, minor, _ = match.groups()

        # Create a dictionary to store the elements
        version_dict: VersionDescriptor = {
            "major": int(major) if major else None,
            "intermediate": int(intermediate) if intermediate else None,
            "minor": int(minor) if minor else None,
            "pre_build_type": pre_build_type,
            "pre_build_number": pre_build_number,
        }
    except Exception:
        return None

    return version_dict


def version_increment(
    version: str,
    type: str = UPGRADE_TYPE_MINOR,
    increment: int = 1,
    build: bool = False,
) -> str:
    version_dict = version_parse(version)

    # Increment according to type
    if type == UPGRADE_TYPE_MAJOR:
        version_dict["major"] = str(int(version_dict["major"]) + increment)
        version_dict["intermediate"], version_dict["minor"] = "0", "0"
    elif type == UPGRADE_TYPE_INTERMEDIATE:
        version_dict["intermediate"] = str(
            int(version_dict["intermediate"]) + increment
        )
        version_dict["minor"] = "0"
    # Any of pre-build version
    elif type in [
        UPGRADE_TYPE_ALPHA,
        UPGRADE_TYPE_BETA,
        UPGRADE_TYPE_DEV,
        UPGRADE_TYPE_RC,
        UPGRADE_TYPE_NIGHTLY,
        UPGRADE_TYPE_SNAPSHOT,
    ]:
        version_dict["pre_build_number"] += increment
    # type == 'version_dict['minor']' or everything else
    else:
        version_dict["minor"] = str(int(version_dict["minor"]) + increment)

    # Set to zero if result is negative
    if int(version_dict["major"]) < 0:
        version_dict["major"], version_dict["intermediate"], version_dict["minor"] = (
            "1",
            "0",
            "0",
        )
    elif int(version_dict["intermediate"]) < 0:
        version_dict["intermediate"], version_dict["minor"] = "0", "0"
    elif int(version_dict["minor"]) < 0:
        version_dict["minor"] = "0"

    return version_join(version_dict, build)
