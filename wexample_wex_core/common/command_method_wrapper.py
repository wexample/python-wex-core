from dataclasses import field
from typing import List

from pydantic import BaseModel

from wexample_helpers.const.types import AnyCallable
from wexample_wex_core.common.command_option import CommandOption


class CommandMethodWrapper(BaseModel):
    function: AnyCallable
    options: List[CommandOption] = field(default_factory=list)

    def set_option(self, option: "CommandOption") -> None:
        self.options.append(option)
