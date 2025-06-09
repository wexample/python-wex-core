from dataclasses import field
from typing import List, Optional

from pydantic import BaseModel

from wexample_helpers.const.types import AnyCallable
from wexample_wex_core.command.middleware_executor import MiddlewareExecutor
from wexample_wex_core.common.command_option import CommandOption


class CommandMethodWrapper(BaseModel):
    function: AnyCallable
    options: List[CommandOption] = field(default_factory=list)
    middlewares: List[MiddlewareExecutor] = field(default_factory=list)

    def set_option(self, option: "CommandOption") -> None:
        self.options.append(option)

    def set_middleware(self, middleware: "MiddlewareExecutor") -> None:
        self.middlewares.append(middleware)

    def find_option_by_name(self, name: str) -> Optional["CommandOption"]:
        """Find an option by its name."""
        for option in self.options:
            if option.kebab_name == name:
                return option
        return None

    def find_option_by_short_name(self, short_name: str) -> Optional["CommandOption"]:
        """Find an option by its short name."""
        for option in self.options:
            if option.short_name == short_name:
                return option
        return None
