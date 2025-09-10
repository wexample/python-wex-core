from __future__ import annotations

from typing import TYPE_CHECKING, cast

from wexample_helpers.service.mixins.registry_container_mixin import (
    RegistryContainerMixin,
)

if TYPE_CHECKING:
    from wexample_wex_core.middleware.abstract_middleware import AbstractMiddleware

from wexample_helpers.decorator.base_class import base_class


@base_class
class MiddlewaresRegistry(RegistryContainerMixin):
    """Middleware configuration for command execution.

    Middlewares can modify the behavior of commands, such as by iterating over
    multiple values for a single option, running in parallel, etc.
    """

    def __attrs_post_init__(self) -> None:
        self._init_middlewares()

    def create_middleware_instance(self, name: str) -> None:
        from wexample_app.service.service_registry import ServiceRegistry

        cast(ServiceRegistry, self.get_registry("middlewares").get(name))

    def _get_middlewares_classes(self) -> list[type[AbstractMiddleware]]:
        from wexample_wex_core.middleware.each_directory_middleware import (
            EachDirectoryMiddleware,
        )
        from wexample_wex_core.middleware.each_file_middleware import EachFileMiddleware
        from wexample_wex_core.middleware.each_path_middleware import EachPathMiddleware

        return [
            EachDirectoryMiddleware,
            EachFileMiddleware,
            EachPathMiddleware,
        ]

    def _init_middlewares(self) -> None:
        self.register_items("middlewares", self._get_middlewares_classes())
