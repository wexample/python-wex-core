from __future__ import annotations

from abc import ABC
from pathlib import Path
from typing import TYPE_CHECKING

from wexample_app.resolver.abstract_command_resolver import (
    AbstractCommandResolver as BaseAbstractCommandResolver,
)
from wexample_helpers.classes.abstract_method import abstract_method

if TYPE_CHECKING:
    from wexample_app.common.command_request import CommandRequest
    from wexample_helpers.const.types import Kwargs, StringsList, StructuredData

    from wexample_wex_core.common.command_address import CommandAddress
    from wexample_wex_core.common.command_method_wrapper import CommandMethodWrapper
    from wexample_wex_core.const.registries import RegistryAddonData
    from wexample_wex_core.context.execution_context import ExecutionContext
    from wexample_wex_core.middleware.abstract_middleware import AbstractMiddleware


class AbstractCommandResolver(BaseAbstractCommandResolver, ABC):
    @classmethod
    def address_to_command(cls, address: CommandAddress) -> str:
        """Convert a CommandAddress to its command string representation."""
        from wexample_helpers.helpers.string import string_to_kebab_case

        from wexample_wex_core.const.globals import (
            COMMAND_SEPARATOR_ADDON,
            COMMAND_SEPARATOR_GROUP,
        )

        return (
            f"{string_to_kebab_case(address.addon)}"
            f"{COMMAND_SEPARATOR_ADDON}"
            f"{string_to_kebab_case(address.group)}"
            f"{COMMAND_SEPARATOR_GROUP}"
            f"{string_to_kebab_case(address.name)}"
        )

    @classmethod
    def build_command_from_function(cls, command_wrapper: CommandMethodWrapper):
        parts = cls.build_command_parts_from_function_name(
            command_wrapper.function.__name__
        )

        return cls.build_command_from_parts(parts)

    @classmethod
    def build_command_from_parts(cls, parts: StringsList) -> str:
        """
        Returns the "default" format (addons style)
        """
        from wexample_helpers.helpers.string import string_to_kebab_case

        from wexample_wex_core.const.globals import (
            COMMAND_SEPARATOR_ADDON,
            COMMAND_SEPARATOR_GROUP,
        )

        # Convert each part to kebab-case
        kebab_parts = [string_to_kebab_case(part) for part in parts]

        return f"{kebab_parts[0]}{COMMAND_SEPARATOR_ADDON}{kebab_parts[1]}{COMMAND_SEPARATOR_GROUP}{kebab_parts[2]}"

    @classmethod
    def build_command_parts_from_function_name(cls, function_name: str) -> StringsList:
        """
        Returns the "default" format (addons style)
        """
        from wexample_wex_core.const.globals import COMMAND_SEPARATOR_FUNCTION_PARTS

        return function_name.split(COMMAND_SEPARATOR_FUNCTION_PARTS)[:3]

    def build_execution_context(
        self,
        middleware: AbstractMiddleware | None,
        command_wrapper: CommandMethodWrapper,
        request: CommandRequest,
        function_kwargs: Kwargs,
    ) -> ExecutionContext:
        from wexample_wex_core.context.execution_context import ExecutionContext

        return ExecutionContext(
            middleware=middleware,
            command_wrapper=command_wrapper,
            request=request,
            function_kwargs=function_kwargs,
        )

    def build_new_command_target(
        self, command: str, extension: str
    ) -> tuple[Path, dict] | None:
        """Return ``(target_path, template_vars)`` for creating a new command file.

        ``template_vars`` must include ``_type`` (template name without extension).
        Return ``None`` if this resolver does not support command creation or the
        command string does not match this resolver's pattern.
        """
        return None

    @abstract_method
    def build_registry_data(self) -> StructuredData:
        pass

    def supports(self, request: CommandRequest) -> object:
        # Alias resolution takes priority — checked before direct pattern match.
        registry = self.kernel.get_configuration_registry()
        if registry.get_addon_commands():
            canonical = self._resolve_alias(request.name)
            if canonical:
                request.name = canonical
                return self.build_match(canonical)

        # Unqualified fallback (v5-style): "group/name" → search all addons.
        # Runs regardless of whether the registry is loaded.
        canonical = self._resolve_unqualified(request.name)
        if canonical:
            request.name = canonical
            return self.build_match(canonical)

        match = self.build_match(request.name)
        # Reject a match where the addon prefix is absent — unqualified commands
        # must be resolved via _resolve_unqualified, not left with a None addon.
        if match and hasattr(match, "group") and not match.group(1):
            return None
        return match

    def _resolve_alias(self, name: str) -> str | None:
        for addon_data in (
            self.kernel.get_configuration_registry().get_addon_commands().values()
        ):
            for cmd_data in addon_data.values():
                if name in cmd_data.get("alias", []):
                    return cmd_data["command"]
        return None

    def _resolve_unqualified(self, name: str) -> str | None:
        """If name has no addon prefix, search all loaded addons for a unique match.

        ``app/started`` → ``app::app/started`` if unique across all addons.
        Raises an error if multiple addons define the same group/name.
        Scans addon workdirs directly so it works even before registry/build.
        """
        from wexample_wex_core.const.globals import COMMAND_SEPARATOR_ADDON

        if COMMAND_SEPARATOR_ADDON in name or "/" not in name:
            return None

        parts = name.split("/")
        if len(parts) != 2:
            return None

        group, cmd_name = parts
        matches = []

        for addon in self.kernel.get_addons().values():
            commands_base = addon.workdir.get_path() / "commands"
            for ext in ("py", "yml"):
                from wexample_helpers.helpers.string import (
                    string_to_kebab_case,
                    string_to_snake_case,
                )

                if (
                    commands_base
                    / string_to_snake_case(group)
                    / f"{string_to_snake_case(cmd_name)}.{ext}"
                ).exists():
                    addon_name = string_to_kebab_case(
                        addon.get_snake_short_class_name()
                    )
                    matches.append(f"{addon_name}{COMMAND_SEPARATOR_ADDON}{name}")
                    break

        if len(matches) == 1:
            return matches[0]

        if len(matches) > 1:
            from wexample_app.exception.app_runtime_exception import AppRuntimeException

            raise AppRuntimeException(
                f"Ambiguous command '{name}' found in multiple addons: {', '.join(matches)}. Use the full form addon::{name}."
            )

        return None

    def _scan_commands_dir(
        self, commands_base: Path, addon_name: str
    ) -> RegistryAddonData:
        """Scan a commands directory and return registry data for all commands found.

        Handles both ``.py`` and ``.yml`` files. Shared by all file-based resolvers.
        """
        import importlib.util

        import yaml

        from wexample_wex_core.common.command_address import CommandAddress
        from wexample_wex_core.common.command_method_wrapper import CommandMethodWrapper
        from wexample_wex_core.const.registries import RegistryCommandData

        addon_data: RegistryAddonData = {}

        if not commands_base.is_dir():
            return addon_data

        tests_base = commands_base.parent / "tests"

        for group_dir in sorted(commands_base.iterdir()):
            if not group_dir.is_dir() or group_dir.name.startswith("_"):
                continue

            for cmd_file in sorted(group_dir.iterdir()):
                if cmd_file.name.startswith("_"):
                    continue
                if cmd_file.suffix not in (".py", ".yml"):
                    continue

                address = CommandAddress.from_path(
                    path=cmd_file,
                    addon_name=addon_name,
                    commands_base=commands_base,
                )
                test_path = tests_base / address.to_relative_path()

                description: str | None = None
                aliases: list[str] = []
                attachments: dict[str, list] = {"before": [], "after": []}
                sudo: bool = False

                if cmd_file.suffix == ".py":
                    func_name = address.to_function_name()
                    spec = importlib.util.spec_from_file_location(func_name, cmd_file)
                    if spec and spec.loader:
                        mod = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(mod)  # type: ignore[union-attr]
                        wrapper = getattr(mod, func_name, None)
                        if isinstance(wrapper, CommandMethodWrapper):
                            description = wrapper.description
                            aliases = list(wrapper.aliases)
                            attachments = {
                                pos: list(items)
                                for pos, items in wrapper.attachments.items()
                            }
                            sudo = wrapper.sudo

                elif cmd_file.suffix == ".yml":
                    with open(cmd_file) as f:
                        yaml_data = yaml.safe_load(f) or {}
                    description = yaml_data.get("description")
                    for dec in yaml_data.get("decorators", []):
                        dec_name = dec.get("name")
                        dec_args = dec.get("args", {})
                        if dec_name == "sudo":
                            sudo = True
                        elif dec_name == "alias":
                            aliases.append(
                                dec_args if isinstance(dec_args, str) else str(dec_args)
                            )
                        elif dec_name == "attach" and isinstance(dec_args, dict):
                            position = dec_args.get("position", "after")
                            attachments[position].append(
                                {
                                    "command": dec_args.get("command", ""),
                                    "pass_args": dec_args.get("pass_args", False),
                                }
                            )

                addon_data[address.to_command_key()] = RegistryCommandData(
                    command=self.address_to_command(address),
                    path=str(cmd_file),
                    test=str(test_path) if test_path.exists() else None,
                    description=description,
                    alias=aliases,
                    attachments=attachments,
                    sudo=sudo,
                )

        return addon_data
