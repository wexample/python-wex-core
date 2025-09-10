from __future__ import annotations

from wexample_helpers.classes.base_class import BaseClass
from wexample_helpers.classes.field import public_field
from wexample_helpers.const.types import AnyCallable, Kwargs
from wexample_helpers.decorator.base_class import base_class
from wexample_wex_core.command.option import Option
from wexample_wex_core.middleware.abstract_middleware import AbstractMiddleware


@base_class
class CommandMethodWrapper(BaseClass):
    description: str | None = public_field(
        default=None,
        description="Optional human-readable description of the command method",
    )
    function: AnyCallable = public_field(
        description="Callable object implementing the command method",
    )
    middlewares: list[AbstractMiddleware] = public_field(
        factory=list,
        description="List of middleware instances applied to the command method",
    )
    middlewares_attributes: dict[str, Kwargs] = public_field(
        factory=dict,
        description="Mapping of middleware names to their initialization attributes",
    )
    options: list[Option] = public_field(
        factory=list,
        description="List of command options available for this method",
    )

    def find_option_by_kebab_name(self, kabab_name: str) -> Option | None:
        """Find an option by its name."""
        for option in self.options:
            if option.kebab_name == kabab_name:
                return option
        return None

    def find_option_by_name(self, name: str) -> Option | None:
        """Find an option by its name."""
        for option in self.options:
            if option.name == name:
                return option
        return None

    def find_option_by_short_name(self, short_name: str) -> Option | None:
        """Find an option by its short name."""
        for option in self.options:
            if option.short_name == short_name:
                return option
        return None

    def get_options_names(self) -> list[str]:
        options = []
        for option in self.options:
            options.append(option.name)

        return options

    def register_middleware(self, name: str, middleware_kwargs: Kwargs) -> None:
        self.middlewares_attributes[name] = middleware_kwargs

    def set_middleware(self, middleware: AbstractMiddleware) -> None:
        self.middlewares.append(middleware)

        for option in middleware.normalized_options:
            self.set_option(option)

    def set_option(self, option: Option) -> None:
        self.options.append(option)
