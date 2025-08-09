# import pytest
#
# from wexample_wex_core.const.types import (
#     VersionDescriptor, UPGRADE_TYPE_MINOR, UPGRADE_TYPE_MAJOR,
#     UPGRADE_TYPE_INTERMEDIATE, UPGRADE_TYPE_ALPHA, UPGRADE_TYPE_BETA
# )
# from wexample_wex_core.helpers.version import (
#     is_greater_than,
#     version_join,
#     version_parse,
#     version_increment
# )
#
#
# def test_version_parse():
#     # Test basic versions
#     assert version_parse("1.2.3") == {
#         "major": 1,
#         "intermediate": 2,
#         "minor": 3,
#         "pre_build_type": None,
#         "pre_build_number": None
#     }
#
#     # Test pre-release versions
#     assert version_parse("1.2.3-beta.1") == {
#         "major": 1,
#         "intermediate": 2,
#         "minor": 3,
#         "pre_build_type": "beta",
#         "pre_build_number": 1
#     }
#
#     # Test partial versions
#     assert version_parse("1.2") == {
#         "major": 1,
#         "intermediate": 2,
#         "minor": None,
#         "pre_build_type": None,
#         "pre_build_number": None
#     }
#
#     # Test invalid versions
#     assert version_parse("invalid") is None
#     assert version_parse("1.2.three") is None
#
#
# def test_version_join():
#     # Test basic version
#     version: VersionDescriptor = {
#         "major": 1,
#         "intermediate": 2,
#         "minor": 3,
#         "pre_build_type": None,
#         "pre_build_number": None
#     }
#     assert version_join(version) == "1.2.3"
#
#     # Test pre-release version
#     version = {
#         "major": 1,
#         "intermediate": 2,
#         "minor": 3,
#         "pre_build_type": "beta",
#         "pre_build_number": 1
#     }
#     assert version_join(version) == "1.2.3-beta.1"
#
#
# def test_is_greater_than():
#     v1: VersionDescriptor = {
#         "major": 2,
#         "intermediate": 0,
#         "minor": 0,
#         "pre_build_type": None,
#         "pre_build_number": None
#     }
#     v2: VersionDescriptor = {
#         "major": 1,
#         "intermediate": 9,
#         "minor": 9,
#         "pre_build_type": None,
#         "pre_build_number": None
#     }
#
#     # Test major version comparison
#     assert is_greater_than(v1, v2)
#     assert not is_greater_than(v2, v1)
#
#     # Test equal versions
#     assert is_greater_than(v1, v1, true_if_equal=True)
#     assert not is_greater_than(v1, v1, true_if_equal=False)
#
#     # Test pre-release versions
#     v3: VersionDescriptor = {
#         "major": 2,
#         "intermediate": 0,
#         "minor": 0,
#         "pre_build_type": "beta",
#         "pre_build_number": 1
#     }
#     assert is_greater_than(v1, v3)  # Release is greater than pre-release
#
#
# def test_version_increment():
#     # Test minor increment
#     assert version_increment("1.2.3") == "1.2.4"
#
#     # Test major increment
#     assert version_increment("1.2.3", type=UPGRADE_TYPE_MAJOR) == "2.0.0"
#
#     # Test intermediate increment
#     assert version_increment("1.2.3", type=UPGRADE_TYPE_INTERMEDIATE) == "1.3.0"
#
#     # Test pre-release increment
#     assert version_increment("1.2.3", type=UPGRADE_TYPE_BETA) == "1.2.3-beta.1"
#
#     # Test increment by more than 1
#     assert version_increment("1.2.3", increment=2) == "1.2.5"
#
#     # Test invalid version
#     with pytest.raises(Exception):
#         version_increment("invalid")
