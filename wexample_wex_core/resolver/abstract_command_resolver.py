from abc import ABC
from typing import TYPE_CHECKING, Type

from wexample_app.resolver.abstract_command_resolver import AbstractCommandResolver as BaseAbstractCommandResolver

if TYPE_CHECKING:
    from wexample_wex_core.common.command import Command


class AbstractCommandResolver(BaseAbstractCommandResolver, ABC):
    def get_command_class_type(cls) -> Type["Command"]:
        from wexample_wex_core.common.command import Command
        return Command
