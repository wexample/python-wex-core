from abc import ABC
from typing import TYPE_CHECKING, Type

from wexample_app.resolver.abstract_command_resolver import AbstractCommandResolver as BaseAbstractCommandResolver

if TYPE_CHECKING:
    from wexample_wex_core.common.command_executor import CommandExecutor


class AbstractCommandResolver(BaseAbstractCommandResolver, ABC):
    def get_command_class_type(cls) -> Type["CommandExecutor"]:
        from wexample_wex_core.common.command_executor import CommandExecutor
        return CommandExecutor
