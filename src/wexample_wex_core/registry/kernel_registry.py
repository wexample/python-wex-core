from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_app.common.abstract_kernel_child import AbstractKernelChild
from wexample_helpers.classes.base_class import BaseClass
from wexample_helpers.classes.mixin.serializable_mixin import SerializableMixin
from wexample_helpers.classes.private_field import private_field
from wexample_helpers.decorator.base_class import base_class

if TYPE_CHECKING:
    from wexample_helpers.const.types import StructuredData

    from wexample_wex_core.const.registries import RegistryAddonData, RegistryCommandData, RegistryResolverData


@base_class
class KernelRegistry(AbstractKernelChild, SerializableMixin, BaseClass):
    _env: str = private_field(description="The environment name")
    _resolvers: RegistryResolverData = private_field(
        factory=dict,
        description="Resolver data loaded from file or built from filesystem scan",
    )

    def __attrs_post_init__(self) -> None:
        from wexample_app.const.globals import ENV_VAR_NAME_APP_ENV

        self._env = self.kernel.get_env_parameter(ENV_VAR_NAME_APP_ENV)

    def get_addon_commands(self) -> RegistryAddonData:
        return self._resolvers.get("addon", {})

    def get_all_commands(self) -> dict[str, RegistryCommandData]:
        """Flat dict of all commands across all resolvers, keyed by command name."""
        return {
            cmd["command"]: cmd
            for resolver in self._resolvers.values()
            for addon in resolver.values()
            for cmd in addon.values()
        }

    def get_all_command_names(self) -> list[str]:
        """All command names including aliases, for autocomplete."""
        names = []
        for cmd in self.get_all_commands().values():
            names.append(cmd["command"])
            names.extend(cmd.get("alias", []))
        return names

    def get_sudo_commands(self) -> dict[str, RegistryCommandData]:
        """All commands that require sudo."""
        return {
            name: cmd
            for name, cmd in self.get_all_commands().items()
            if cmd.get("sudo")
        }

    def find_command(self, name: str) -> RegistryCommandData | None:
        """Find a command by exact name or alias."""
        all_commands = self.get_all_commands()
        if name in all_commands:
            return all_commands[name]
        for cmd in all_commands.values():
            if name in cmd.get("alias", []):
                return cmd
        return None

    def suggest(self, prefix: str) -> list[str]:
        """Return all command names (and aliases) matching the given prefix."""
        return [name for name in self.get_all_command_names() if name.startswith(prefix)]

    def hydrate(self, data: StructuredData) -> None:
        self._env = data.get("env", self._env)
        self._resolvers = data.get("resolvers", {})

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

        self._resolvers = resolvers

        return {"env": self._env, "resolvers": resolvers}
