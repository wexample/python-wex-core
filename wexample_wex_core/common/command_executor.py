from typing import TYPE_CHECKING

from wexample_app.common.command import Command
from wexample_wex_core.common.command_method_wrapper import CommandMethodWrapper

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
        function_kwargs = {
            "kernel": self.kernel
        }

        for option in self.command_wrapper.options:
            if not option.name in function_kwargs and option.default is not None:
                function_kwargs[option.name] = option.default

        return self.function(
            **function_kwargs
        )
