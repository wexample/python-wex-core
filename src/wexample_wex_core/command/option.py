from __future__ import annotations

from typing import Any

from wexample_helpers.classes.base_class import BaseClass
from wexample_helpers.classes.field import public_field
from wexample_helpers.decorator.base_class import base_class


@base_class
class Option(BaseClass):
    default: Any = public_field(
        default=None,
        description="Default value for the option if none is provided",
    )
    description: str | None = public_field(
        default=None,
        description="Optional human-readable description of the option",
    )
    is_flag: bool = public_field(
        default=False,
        description="Indicates whether the option is a boolean flag",
    )
    kebab_name: str | None = public_field(
        default=None,
        description="Option name in kebab-case format (e.g., --some-option)",
    )
    name: str = public_field(
        description="Canonical name of the option",
    )
    required: bool = public_field(
        default=False,
        description="Indicates whether this option must be provided",
    )
    short_name: str | None = public_field(
        default=None,
        description="Optional single-letter shorthand for the option (e.g., -o)",
    )
    type: type = public_field(
        description="Expected Python type for the option value",
    )
    value: Any = public_field(
        default=None,
        description="The computed value resolved from input arguments or default",
    )

    def __attrs_post_init__(self) -> None:
        from wexample_helpers.helpers.string import string_to_kebab_case
        from wexample_wex_core.helpers.option import option_build_short_name

        self.kebab_name = string_to_kebab_case(self.name)
        self.short_name = option_build_short_name(self.name)
