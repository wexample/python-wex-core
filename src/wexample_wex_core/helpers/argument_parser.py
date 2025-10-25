from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from wexample_app.command.option import Option

ParsedArgs = dict[str, Any]


def parse_arguments(
    arguments: list[str],
    options: list[Option],
    allowed_option_names: list[str] | None = None,
) -> ParsedArgs:
    """Parse raw command line arguments into a dictionary of option name to value.

    Args:
        arguments: List of command line arguments to parse
        options: List of Option objects defining the available options
        allowed_option_names: Optional list of allowed option names for error messages

    Returns:
        Dictionary mapping option names to their parsed values

    Raises:
        CommandUnexpectedArgumentException: If an unknown argument is encountered
        CommandArgumentConversionException: If argument value conversion fails
    """
    from wexample_helpers.helpers.cli import cli_argument_convert_value

    from wexample_wex_core.exception.command_argument_conversion_exception import (
        CommandArgumentConversionException,
    )
    from wexample_wex_core.exception.command_unexpected_argument_exception import (
        CommandUnexpectedArgumentException,
    )

    # Helper functions to find options
    def find_option_by_kebab_name(kebab_name: str) -> Option | None:
        for option in options:
            if option.kebab_name == kebab_name:
                return option
        return None

    def find_option_by_short_name(short_name: str) -> Option | None:
        for option in options:
            if option.short_name == short_name:
                return option
        return None

    result: dict[str, Any] = {}
    skip_next = False

    for i, arg in enumerate(arguments):
        # Skip this iteration if we've already processed this argument as a value
        if skip_next:
            skip_next = False
            continue

        # Check if the argument is an option (starts with - or --)
        if arg.startswith("--"):
            # Long option name (e.g., --version)
            option_name = arg[2:]
            option = find_option_by_kebab_name(option_name)

            if not option:
                # Raise exception for unexpected argument
                raise CommandUnexpectedArgumentException(
                    argument=arg,
                    allowed_arguments=allowed_option_names or [],
                )

            # Process the option
            if option.is_flag:
                result[option.name] = True
            elif i + 1 < len(arguments) and not arguments[i + 1].startswith("-"):
                try:
                    result[option.name] = cli_argument_convert_value(
                        arguments[i + 1], option.type
                    )
                    skip_next = True
                except Exception as e:
                    raise CommandArgumentConversionException(
                        argument_name=option.name,
                        value=arguments[i + 1],
                        target_type=option.type,
                        cause=e,
                    )
            else:
                result[option.name] = (
                    option.default if option.default is not None else None
                )

        elif arg.startswith("-") and len(arg) > 1:
            # Short option name (e.g., -v)
            short_name = arg[1:]
            option = find_option_by_short_name(short_name)

            if not option:
                # Raise exception for unexpected argument
                raise CommandUnexpectedArgumentException(
                    argument=arg,
                    allowed_arguments=allowed_option_names or [],
                )

            # Process the option
            if option.is_flag:
                result[option.name] = True
            elif i + 1 < len(arguments) and not arguments[i + 1].startswith("-"):
                try:
                    result[option.name] = cli_argument_convert_value(
                        arguments[i + 1], option.type
                    )
                    skip_next = True
                except Exception as e:
                    raise CommandArgumentConversionException(
                        argument_name=option.name,
                        value=arguments[i + 1],
                        target_type=option.type,
                        cause=e,
                    )
            else:
                result[option.name] = (
                    option.default if option.default is not None else None
                )

    return result
