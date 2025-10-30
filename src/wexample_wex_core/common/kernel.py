from __future__ import annotations

from typing import TYPE_CHECKING, cast

from wexample_app.common.abstract_kernel import AbstractKernel
from wexample_app.common.mixins.command_line_kernel import CommandLineKernel
from wexample_app.common.mixins.command_runner_kernel import CommandRunnerKernel
from wexample_helpers.classes.private_field import private_field
from wexample_helpers.decorator.base_class import base_class
from wexample_prompt.enums.verbosity_level import VerbosityLevel

if TYPE_CHECKING:
    from wexample_app.command.option import Option
    from wexample_app.const.types import CommandLineArgumentsList
    from wexample_app.resolver.abstract_command_resolver import AbstractCommandResolver
    from wexample_app.runner.abstract_command_runner import AbstractCommandRunner
    from wexample_config.const.types import DictConfig
    from wexample_filestate.utils.file_state_manager import FileStateManager
    from wexample_prompt.common.io_manager import IoManager
    from wexample_wex_core.common.abstract_addon_manager import AbstractAddonManager
    from wexample_wex_core.common.command_request import CommandRequest
    from wexample_wex_core.registry.kernel_registry import KernelRegistry
    from wexample_wex_core.workdir.kernel_workdir import KernelWorkdir


@base_class
class Kernel(CommandRunnerKernel, CommandLineKernel, AbstractKernel):
    _config_arg_indentation_level: int | None = private_field(
        default=None,
        description="Prompt messages indentation level",
    )
    _config_arg_verbosity: VerbosityLevel = private_field(
        default=VerbosityLevel.DEFAULT,
        description="Verbosity level of every logs",
    )
    _config_arg_output_format: None | list[str] = private_field(
        default=None,
        description="Verbosity level of every logs",
    )
    _config_arg_output_target: None | list[str] = private_field(
        default=None,
        description="A target where to place the output",
    )
    _registry: KernelRegistry = private_field(description="The configuration registry")

    def get_addons(self) -> dict[str, AbstractAddonManager]:
        from wexample_wex_core.const.registries import REGISTRY_KERNEL_ADDON

        return self.get_registry(REGISTRY_KERNEL_ADDON).get_all()

    def _get_available_output_handlers(self):
        """Get available output handlers for core kernel.
        
        Returns:
            Dictionary with stdout and file handlers
        """
        from wexample_app.output.app_stdout_output_handler import (
            AppStdoutOutputHandler,
        )
        from wexample_wex_core.output.extended_file_output_handler import (
            ExtendedFileOutputHandler,
        )

        return {
            "stdout": AppStdoutOutputHandler,
            "file": ExtendedFileOutputHandler,
        }

    def execute_kernel_command_and_print(self, request: CommandRequest) -> None:
        """Execute a command and print its response using the appropriate output handler.
        
        Overrides parent to handle output_target from core CommandRequest.
        
        Args:
            request: The command request to execute
        """
        from pathlib import Path

        from wexample_app.output.app_file_output_handler import AppFileOutputHandler
        from wexample_wex_core.common.command_request import (
            CommandRequest as CoreCommandRequest,
        )

        response = self.execute_kernel_command(request=request)
        
        # Check if this is a core request with output_target
        if isinstance(request, CoreCommandRequest) and request.output_target:
            target = request.output_target[0] if request.output_target else "stdout"
            
            if target == "file":
                # Use file output handler
                file_path = Path(f"output_{request.request_id}.txt")
                file_handler = AppFileOutputHandler(file_path=file_path)
                file_handler.print(response=response)
                self.io.success(f"Output written to {file_path}")
            else:
                # Default to stdout
                self.output.print(response=response)
        else:
            # Fallback to parent behavior
            self.output.print(response=response)

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
                output_target=self._config_arg_output_target,
                output_format=self._config_arg_output_format,
            )
        ]

    def _create_workdir_state_manager(
        self,
        entrypoint_path: str,
        io: IoManager,
        config: DictConfig | None = None,
    ) -> FileStateManager:
        return self._get_workdir_state_manager_class().create_from_kernel(
            kernel=self, config=config or {}, io=io
        )

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

    def _get_core_args(self) -> list[Option]:
        from wexample_app.command.option import Option
        from wexample_prompt.enums.verbosity_level import VerbosityLevel

        return super()._get_core_args() + [
            Option(
                name="quiet",
                is_flag=True,
                type=bool,
                value=VerbosityLevel.QUIET,
                description="Silence all output",
            ),
            Option(
                name="v",
                is_flag=True,
                type=bool,
                value=VerbosityLevel.MEDIUM,
                description="Medium verbosity (-v)",
            ),
            Option(
                name="vv",
                is_flag=True,
                type=bool,
                value=VerbosityLevel.HIGH,
                description="High verbosity (-vv)",
            ),
            Option(
                name="vvv",
                is_flag=True,
                type=bool,
                value=VerbosityLevel.MAXIMUM,
                description="Maximum verbosity (-vvv)",
            ),
            Option(
                name="output_format",
                type=str,
                value="str",
                description="The way to render the output",
            ),
            Option(
                name="output_target",
                type=str,
                value="str",
                description="The emplacement where placing the output (stdout, file, ...)",
                multiple=True,
                always_list=True
            ),
            Option(
                name="indentation_level",
                is_flag=False,
                type=int,
                description="Number of indentation levels to use",
            ),
        ]

    def _get_workdir_state_manager_class(self) -> type[KernelWorkdir]:
        from wexample_wex_core.workdir.kernel_workdir import KernelWorkdir

        return KernelWorkdir

    def _init_addons(
        self, addons: list[type[AbstractAddonManager]] | None = None
    ) -> None:
        from wexample_app.service.service_registry import ServiceRegistry
        from wexample_wex_core.const.registries import REGISTRY_KERNEL_ADDON

        cast(ServiceRegistry, self.set_registry(REGISTRY_KERNEL_ADDON))
        registry = self.register_items(REGISTRY_KERNEL_ADDON, addons or [])
        registry.instantiate_all(kernel=self)

    def _init_command_line_kernel(self: AbstractKernel) -> None:
        from wexample_app.output.app_stdout_output_handler import AppStdoutOutputHandler
        from wexample_helpers.helpers.array import array_unique

        super()._init_command_line_kernel()
        # We can then use config.
        self.io.default_context_verbosity = self._config_arg_verbosity
        self.io.indentation = min(
            self._config_arg_indentation_level or self.io.indentation,
            int(self.io.terminal_width / 3),
        )

        self._config_arg_output_format = self._config_arg_output_format or "text"
        self._config_arg_output_target = array_unique(self._config_arg_output_target or [
            AppStdoutOutputHandler.get_name()
        ])

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
