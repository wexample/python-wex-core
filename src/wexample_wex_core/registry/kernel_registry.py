from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_app.common.abstract_kernel_child import AbstractKernelChild
from wexample_helpers.classes.base_class import BaseClass
from wexample_helpers.classes.field import public_field
from wexample_helpers.classes.mixin.serializable_mixin import SerializableMixin

if TYPE_CHECKING:
    from wexample_helpers.const.types import StructuredData


class KernelRegistry(AbstractKernelChild, SerializableMixin, BaseClass):
    env: str = public_field(description="The environment name")

    def __attrs_post_init__(self) -> None:
        from wexample_app.const.globals import ENV_VAR_NAME_APP_ENV

        self.env = self.kernel.get_env_parameter(ENV_VAR_NAME_APP_ENV)

    def hydrate(self, data: StructuredData) -> None:
        self.env = data.get("env", self.env)

    def serialize(self) -> StructuredData:
        from wexample_app.resolver.abstract_command_resolver import (
            AbstractCommandResolver,
        )

        resolvers = {}

        for command_resolver in self.kernel.get_resolvers().values():
            assert isinstance(command_resolver, AbstractCommandResolver)
            resolvers[command_resolver.get_snake_short_class_name()] = (
                command_resolver.build_registry_data()
            )

        return {"env": self.env, "resolvers": resolvers}
