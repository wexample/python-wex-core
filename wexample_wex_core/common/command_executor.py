from typing import TYPE_CHECKING, Dict, Any, List, Optional, Type

from wexample_app.common.command import Command
from wexample_wex_core.common.command_method_wrapper import CommandMethodWrapper
from wexample_wex_core.common.command_option import CommandOption
from wexample_wex_core.exception.command_option_missing_exception import CommandOptionMissingException
from wexample_wex_core.exception.command_unexpected_argument_exception import CommandUnexpectedArgumentException
from wexample_wex_core.exception.command_argument_conversion_exception import CommandArgumentConversionException

if TYPE_CHECKING:
    from wexample_app.common.command_request import CommandRequest


class CommandExecutor(Command):
    command_wrapper: CommandMethodWrapper

    def __init__(self, command_wrapper: CommandMethodWrapper, *args, **kwargs):
        kwargs['command_wrapper'] = command_wrapper

        super().__init__(
            function=command_wrapper.function,
            *args,
            **kwargs
        )

    def execute_request(self, request: "CommandRequest"):
        """Execute the command with the given request arguments."""
        # Parse and convert arguments to appropriate types
        parsed_args = self._parse_arguments(request.arguments)
        
        # Create the function kwargs dictionary with parsed arguments
        function_kwargs = self._build_function_kwargs(parsed_args)
        
        # Add kernel to the kwargs
        function_kwargs["kernel"] = self.kernel
        
        # Execute the function with the processed arguments
        return self.function(**function_kwargs)
    
    def _parse_arguments(self, arguments: List[str]) -> Dict[str, Any]:
        """Parse raw command line arguments into a dictionary of option name to value."""
        result: Dict[str, Any] = {}
        skip_next = False
        
        for i, arg in enumerate(arguments):
            # Skip this iteration if we've already processed this argument as a value
            if skip_next:
                skip_next = False
                continue
                
            # Check if the argument is an option (starts with - or --)
            if arg.startswith('--'):
                # Long option name (e.g., --version)
                option_name = arg[2:]
                option = self._find_option_by_name(option_name)
                
                if not option:
                    # Raise exception for unexpected argument
                    raise CommandUnexpectedArgumentException(argument=arg)
                    
                # Process the option
                if option.is_flag:
                    result[option.name] = True
                elif i + 1 < len(arguments) and not arguments[i + 1].startswith('-'):
                    try:
                        result[option.name] = self._convert_value(arguments[i + 1], option.type)
                        skip_next = True
                    except Exception as e:
                        raise CommandArgumentConversionException(
                            argument_name=option.name,
                            value=arguments[i + 1],
                            target_type=option.type,
                            cause=e
                        )
                else:
                    result[option.name] = option.default if option.default is not None else None
                        
            elif arg.startswith('-') and len(arg) > 1:
                # Short option name (e.g., -v)
                short_name = arg[1:]
                option = self._find_option_by_short_name(short_name)
                
                if not option:
                    # Raise exception for unexpected argument
                    raise CommandUnexpectedArgumentException(argument=arg)
                    
                # Process the option
                if option.is_flag:
                    result[option.name] = True
                elif i + 1 < len(arguments) and not arguments[i + 1].startswith('-'):
                    try:
                        result[option.name] = self._convert_value(arguments[i + 1], option.type)
                        skip_next = True
                    except Exception as e:
                        raise CommandArgumentConversionException(
                            argument_name=option.name,
                            value=arguments[i + 1],
                            target_type=option.type,
                            cause=e
                        )
                else:
                    result[option.name] = option.default if option.default is not None else None
        
        return result
    
    def _find_option_by_name(self, name: str) -> Optional[CommandOption]:
        """Find an option by its name."""
        for option in self.command_wrapper.options:
            if option.name == name:
                return option
        return None
    
    def _find_option_by_short_name(self, short_name: str) -> Optional[CommandOption]:
        """Find an option by its short name."""
        for option in self.command_wrapper.options:
            if option.short_name == short_name:
                return option
        return None
    
    def _convert_value(self, value: str, target_type: Type) -> Any:
        """Convert a string value to the target type."""
        if target_type == bool:
            return value.lower() in ('true', 'yes', 'y', '1', 'on')
        elif target_type == int:
            return int(value)
        elif target_type == float:
            return float(value)
        elif target_type == str:
            return value
        elif target_type == list:
            # Assume comma-separated values
            return [item.strip() for item in value.split(',')]
        else:
            # For custom types, try to use the constructor
            return target_type(value)
    
    def _build_function_kwargs(self, parsed_args: Dict[str, Any]) -> Dict[str, Any]:
        """Build the final kwargs dictionary for the function call."""
        function_kwargs = {}
        
        # Process all declared options
        for option in self.command_wrapper.options:
            # If the option is in parsed args, use that value
            if option.name in parsed_args:
                function_kwargs[option.name] = parsed_args[option.name]
            # Otherwise, use the default value if available
            elif option.default is not None:
                function_kwargs[option.name] = option.default
            # If the option is required but not provided, raise an error
            elif option.required:
                raise CommandOptionMissingException(option_name=option.name)
        
        return function_kwargs
