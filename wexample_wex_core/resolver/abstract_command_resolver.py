from abc import ABC

from wexample_app.resolver.abstract_command_resolver import AbstractCommandResolver as BaseAbstractCommandResolver
from wexample_helpers.const.types import StructuredData


class AbstractCommandResolver(BaseAbstractCommandResolver, ABC):
    def build_registry_data(self) -> StructuredData:
        return {}
