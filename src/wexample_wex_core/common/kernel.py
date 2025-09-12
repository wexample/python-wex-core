from __future__ import annotations

from typing import TYPE_CHECKING, cast

from wexample_app.common.abstract_kernel import AbstractKernel
from wexample_app.common.mixins.command_line_kernel import CommandLineKernel
from wexample_app.common.mixins.command_runner_kernel import CommandRunnerKernel
from wexample_helpers.classes.private_field import private_field
from wexample_helpers.decorator.base_class import base_class

if TYPE_CHECKING:
    from wexample_app.const.types import CommandLineArgumentsList
    from wexample_app.resolver.abstract_command_resolver import AbstractCommandResolver
    from wexample_app.runner.abstract_command_runner import AbstractCommandRunner
    from wexample_config.const.types import DictConfig
    from wexample_filestate.file_state_manager import FileStateManager
    from wexample_prompt.common.io_manager import IoManager
    from wexample_wex_core.common.abstract_addon_manager import AbstractAddonManager
    from wexample_wex_core.common.command_request import CommandRequest
    from wexample_wex_core.registry.kernel_registry import KernelRegistry
    from wexample_prompt.enums.verbosity_level import VerbosityLevel


@base_class
class Kernel(CommandRunnerKernel, CommandLineKernel, AbstractKernel):
    _config_arg_verbosity: VerbosityLevel = private_field(
        default=VerbosityLevel.DEFAULT,
        init=False,
        description="Verbosity level of every logs",
    )
    _registry: KernelRegistry = private_field(
        init=False, description="The configuration registry"
    )

    def get_addons(self) -> dict[str, AbstractAddonManager]:
        from wexample_wex_core.const.registries import REGISTRY_KERNEL_ADDON

        return self.get_registry(REGISTRY_KERNEL_ADDON).get_all()

    def get_configuration_registry(self) -> KernelRegistry:
        return self._registry

    def setup(
        self, addons: list[type[AbstractAddonManager]] | None = None
    ) -> AbstractKernel:
        response = super().setup()

        self._init_command_line_kernel()
        self._init_addons(addons=addons)
        self._init_resolvers()
        self._init_runners()
        self._init_middlewares()
        self._init_registry()

        return response

    def _build_single_command_request_from_arguments(
        self, arguments: CommandLineArgumentsList
    ):
        # Core command request takes a request id.
        return [
            self._get_command_request_class()(
                kernel=self,
                request_id=arguments[0],
                name=arguments[1],
                arguments=arguments[2:],
            )
        ]

    def _get_command_request_class(self) -> type[CommandRequest]:
        from wexample_wex_core.common.command_request import CommandRequest

        return CommandRequest

    def _get_command_resolvers(self) -> list[type[AbstractCommandResolver]]:
        from wexample_wex_core.resolver.addon_command_resolver import (
            AddonCommandResolver,
        )
        from wexample_wex_core.resolver.service_command_resolver import (
            ServiceCommandResolver,
        )

        return [
            # filestate: python-iterable-sort
            AddonCommandResolver,
            ServiceCommandResolver,
        ]

    def _get_command_runners(self) -> list[type[AbstractCommandRunner]]:
        from wexample_wex_core.runner.core_python_command_runner import (
            CorePythonCommandRunner,
        )
        from wexample_wex_core.runner.core_yaml_command_runner import (
            CoreYamlCommandRunner,
        )

        return [
            # Default runner.
            # filestate: python-iterable-sort
            CorePythonCommandRunner,
            CoreYamlCommandRunner,
        ]

    def _get_core_args(self):
        from wexample_prompt.enums.verbosity_level import VerbosityLevel
        return super()._get_core_args() + [
            {"arg": "quiet", "attr": "verbosity", "value": VerbosityLevel.QUIET},
            {"arg": "vv", "attr": "verbosity", "value": VerbosityLevel.MEDIUM},
            {"arg": "vvv", "attr": "verbosity", "value": VerbosityLevel.MAXIMUM},
        ]

    def _get_workdir_state_manager_class(
        self,
        entrypoint_path: str,
        io: IoManager,
        config: DictConfig | None = None,
    ) -> FileStateManager:
        from wexample_wex_core.workdir.kernel_workdir import KernelWorkdir

        return KernelWorkdir.create_from_kernel(kernel=self, config=config or {}, io=io)

    def _init_addons(
        self, addons: list[type[AbstractAddonManager]] | None = None
    ) -> None:
        from wexample_app.service.service_registry import ServiceRegistry
        from wexample_wex_core.const.registries import REGISTRY_KERNEL_ADDON

        cast(ServiceRegistry, self.set_registry(REGISTRY_KERNEL_ADDON))
        registry = self.register_items(REGISTRY_KERNEL_ADDON, addons or [])
        registry.instantiate_all(kernel=self)

    def _init_command_line_kernel(self: AbstractKernel) -> None:
        super()._init_command_line_kernel()
        # We can then use config.
        self.io.default_context_verbosity = self._config_arg_verbosity

    def _init_middlewares(self) -> None:
        from wexample_wex_core.common.abstract_addon_manager import AbstractAddonManager

        classes = []
        for addon in self.get_addons().values():
            classes.extend(cast(AbstractAddonManager, addon).get_middlewares_classes())

        self.register_items("middlewares", classes)

    def _init_registry(self) -> None:
        from wexample_wex_core.path.kernel_registry_file import KernelRegistryFile
        from wexample_wex_core.workdir.kernel_workdir import KernelWorkdir

        kernel_registry_file = self.workdir.get_shortcut(
            KernelWorkdir.SHORTCUT_REGISTRY
        )
        assert isinstance(kernel_registry_file, KernelRegistryFile)

        # Registry has zero length.
        if kernel_registry_file.get_local_file().is_empty():
            # Create registry and dump in file
            self._registry = kernel_registry_file.create_registry_and_save(kernel=self)
        else:
            # Fill registry from existing file
            self._registry = kernel_registry_file.create_registry_from_content(
                kernel=self
            )
