from __future__ import annotations

import logging
from typing import TYPE_CHECKING, cast

from wexample_app.common.abstract_kernel import AbstractKernel
from wexample_app.common.mixins.command_line_kernel import CommandLineKernel
from wexample_app.common.mixins.command_runner_kernel import CommandRunnerKernel
from wexample_app.const.output import OUTPUT_FORMAT_STR, OUTPUT_TARGET_NONE
from wexample_app.output.app_none_output_handler import AppNoneOutputHandler
from wexample_helpers.classes.private_field import private_field
from wexample_helpers.decorator.base_class import base_class
from wexample_prompt.enums.verbosity_level import VerbosityLevel

if TYPE_CHECKING:
    from wexample_app.command.option import Option
    from wexample_app.const.types import CommandLineArgumentsList
    from wexample_app.output.abstract_app_output_handler import AbstractAppOutputHandler
    from wexample_app.resolver.abstract_command_resolver import AbstractCommandResolver
    from wexample_app.runner.abstract_command_runner import AbstractCommandRunner
    from wexample_config.const.types import DictConfig
    from wexample_filestate.utils.file_state_manager import FileStateManager
    from wexample_prompt.common.io_manager import IoManager

    from wexample_wex_core.common.abstract_addon_manager import AbstractAddonManager
    from wexample_wex_core.common.command_request import CommandRequest
    from wexample_wex_core.registry.kernel_registry import KernelRegistry
    from wexample_wex_core.workdir.kernel_workdir import KernelWorkdir
    from wexample_wex_core.yaml.script_runner_registry import ScriptRunnerRegistry
    from wexample_wex_core.yaml.step_guard_registry import StepGuardRegistry


@base_class
class Kernel(CommandRunnerKernel, CommandLineKernel, AbstractKernel):
    _config_arg_force_request_id: str | None = private_field(
        default=None,
        description="Force a specific request ID when set by an external process",
    )
    _config_arg_ignore_missing_command: bool = private_field(
        default=False,
        description="Exit silently with code 0 if the command is not found",
    )
    _config_arg_indentation_level: int | None = private_field(
        default=None,
        description="Prompt messages indentation level",
    )
    _config_arg_output_format: None | list[str] = private_field(
        default=None,
        description="Verbosity level of every logs",
    )
    _config_arg_output_target: None | list[str] = private_field(
        default=None,
        description="A target where to place the output",
    )
    _config_arg_quiet: bool = private_field(
        default=False,
        description="Disable verbosity, every log or message, useful to capture structured output",
    )
    _config_arg_subprocess: bool = private_field(
        default=False,
        description="Indicates this process was launched as a subprocess by another wex process",
    )
    _config_arg_v: bool = private_field(
        default=False,
        description="Default verbosity",
    )
    _config_arg_vv: bool = private_field(
        default=False,
        description="High verbosity",
    )
    _config_arg_vvv: bool = private_field(
        default=False,
        description="Maximum verbosity",
    )
    _execution_depth: int = private_field(
        default=0,
        description="Tracks nested execute_kernel_command calls; sudo re-exec only allowed at depth 0",
    )
    _logger: logging.Logger = private_field(
        description="Python logger for operational/debug messages"
    )
    _registry: KernelRegistry = private_field(description="The configuration registry")
    _script_runner_registry: ScriptRunnerRegistry = private_field(
        description="Registry of YAML script runners"
    )
    _step_guard_registry: StepGuardRegistry = private_field(
        description="Registry of YAML step guards contributed by addons"
    )

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    @property
    def script_runner_registry(self) -> ScriptRunnerRegistry:
        return self._script_runner_registry

    @property
    def step_guard_registry(self) -> StepGuardRegistry:
        return self._step_guard_registry

    def create_output_handlers(
        self, targets: list[str] | None = None
    ) -> [AbstractAppOutputHandler]:
        """Initialize output handlers based on targets, falling back to kernel default.

        Args:
            targets: Override targets for this call. Falls back to _config_arg_output_target.
        """
        available_handlers = self._get_available_output_handlers()
        outputs = []

        for target in targets or self._config_arg_output_target:
            if target in available_handlers:
                handler_class = available_handlers[target]
                outputs.append(handler_class(kernel=self))

        return outputs

    def execute_kernel_command(self, request: CommandRequest) -> AbstractResponse:
        pass

        self._execution_depth += 1
        try:
            self._enforce_sudo_if_needed(request)
            self._execute_attached(request, "before")
            response = super().execute_kernel_command(request)

            from wexample_app.response.queued_collection_response import (
                QueuedCollectionResponse,
            )

            if isinstance(response, QueuedCollectionResponse):
                # "after" runs as the last queue step — skipped if the queue stops early.
                # "always_after" runs in finally_steps — guaranteed regardless of stops.
                response.content.append(
                    lambda: self._execute_attached(request, "after")
                )
                response.finally_steps.append(
                    lambda: self._execute_attached(request, "always_after")
                )
            else:
                self._execute_attached(request, "after")
                self._execute_attached(request, "always_after")

            return response
        finally:
            self._execution_depth -= 1

    def get_addons(self) -> dict[str, AbstractAddonManager]:
        from wexample_wex_core.const.registries import REGISTRY_KERNEL_ADDON

        return self.get_registry(REGISTRY_KERNEL_ADDON).get_all()

    def get_configuration_registry(self) -> KernelRegistry:
        return self._registry

    def get_logo(self) -> str | None:
        """Return the CLI logo string, or None if this kernel has no logo defined."""
        return None

    def run_function(
        self,
        wrapper: CommandMethodWrapper,
        arguments: dict | None = None,
        output_target: list[str] | None = None,
    ) -> AbstractResponse:
        from wexample_app.const.output import OUTPUT_TARGET_NONE

        from wexample_wex_core.resolver.abstract_command_resolver import (
            AbstractCommandResolver,
        )

        command_name = AbstractCommandResolver.build_command_from_function(wrapper)
        request = self._get_command_request_class()(
            kernel=self,
            name=command_name,
            arguments=arguments or {},
            output_target=output_target or [OUTPUT_TARGET_NONE],
        )
        return self.execute_kernel_command(request)

    def set_output_target(self, targets: list[str]) -> None:
        self._config_arg_output_target = targets

    def setup(
        self, addons: list[type[AbstractAddonManager]] | None = None
    ) -> AbstractKernel:
        response = super().setup()

        self._init_local_env()
        self._init_command_line_kernel()
        self._init_logging()
        self._init_addons(addons=addons)
        self._auto_detect_env()
        self._init_resolvers()
        self._init_runners()
        self._init_middlewares()
        self._init_registry()
        self._init_script_runner_registry()
        self._init_step_guard_registry()

        print()

        return response

    def _auto_detect_env(self) -> None:
        """Auto-detect missing env vars declared by addons and persist found values.

        Called after _init_addons so addon managers are available. For each key
        declared in addon.get_local_configurable_keys(), if the value is absent
        from os.environ, the detect() callable is tried. Found values are set in
        os.environ, persisted to .wex/local/env.yml, and on_apply() is called.
        For values already present (loaded by _init_local_env or the system
        environment), only on_apply() is called to apply side effects (e.g. PATH).
        """
        import os

        local_env = self.workdir.get_local_data("env")
        changed = False

        for addon in self.get_addons().values():
            for entry in addon.get_local_configurable_keys():
                key = entry["key"]
                detect = entry.get("detect")
                on_apply = entry.get("on_apply")

                value = os.environ.get(key)

                if not value and detect:
                    value = detect()
                    if value:
                        os.environ[key] = value
                        local_env[key] = value
                        changed = True

                if value and on_apply:
                    on_apply(value)

        if changed:
            self.workdir.set_local_data("env", local_env)

    def _build_single_command_request_from_arguments(
        self, arguments: CommandLineArgumentsList
    ):
        kwargs = dict(
            kernel=self,
            name=arguments[0],
            arguments=arguments[1:],
            output_target=self._config_arg_output_target,
            output_format=self._config_arg_output_format,
        )
        if self._config_arg_force_request_id:
            kwargs["request_id"] = self._config_arg_force_request_id
        return [self._get_command_request_class()(**kwargs)]

    def _create_workdir_state_manager(
        self,
        entrypoint_path: str,
        io: IoManager,
        config: DictConfig | None = None,
    ) -> FileStateManager:
        return self._get_workdir_state_manager_class().create_from_kernel(
            kernel=self, config=config or {}, io=io
        )

    def _enforce_sudo_if_needed(self, request: CommandRequest) -> None:
        import os
        import sys

        if os.geteuid() == 0:
            return

        if self._execution_depth > 1:
            return

        for cmd_data in self._get_live_command_registry_entries():
            if cmd_data.get("command") == request.name and cmd_data.get("sudo"):
                os.execvp("sudo", ["sudo", sys.executable] + sys.argv)
                return

    def _execute_attached(self, request: CommandRequest, position: str) -> None:
        target_command = request.name
        for cmd_data in self._get_live_command_registry_entries():
            for attachment in cmd_data.get("attachments", {}).get(position, []):
                if attachment["command"] != target_command:
                    continue

                attached_request = self._get_command_request_class()(
                    kernel=self,
                    name=cmd_data["command"],
                    # Attached commands are independent user-facing events.
                    # They always run at the kernel's configured output level (stdout
                    # for CLI), never silenced by an intermediate sub-request that
                    # uses OUTPUT_TARGET_NONE (e.g. run_function, YAML command: steps).
                    output_target=self._config_arg_output_target,
                    arguments=(
                        request.arguments if attachment.get("pass_args") else {}
                    ),
                )
                self.execute_kernel_command_and_print(attached_request)

    def _get_available_output_handlers(self):
        """Get available output handlers for core kernel.

        Returns:
            Dictionary with stdout and file handlers
        """
        from wexample_app.const.output import OUTPUT_TARGET_FILE, OUTPUT_TARGET_STDOUT
        from wexample_app.output.app_stdout_output_handler import (
            AppStdoutOutputHandler,
        )

        from wexample_wex_core.output.request_file_output_handler import (
            RequestFileOutputHandler,
        )

        return {
            OUTPUT_TARGET_NONE: AppNoneOutputHandler,
            OUTPUT_TARGET_STDOUT: AppStdoutOutputHandler,
            OUTPUT_TARGET_FILE: RequestFileOutputHandler,
        }

    def _get_command_request_class(self) -> type[CommandRequest]:
        from wexample_wex_core.common.command_request import CommandRequest

        return CommandRequest

    def _get_command_resolvers(self) -> list[type[AbstractCommandResolver]]:
        from wexample_wex_core.common.abstract_addon_manager import AbstractAddonManager
        from wexample_wex_core.resolver.addon_command_resolver import (
            AddonCommandResolver,
        )
        from wexample_wex_core.resolver.user_command_resolver import UserCommandResolver

        resolvers: list[type[AbstractCommandResolver]] = [
            # filestate: python-iterable-sort
            AddonCommandResolver,
            UserCommandResolver,
        ]

        for addon in self.get_addons().values():
            resolvers.extend(
                cast(AbstractAddonManager, addon).get_command_resolver_classes()
            )

        return resolvers

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
                short_name="v",
                is_flag=True,
                type=bool,
                value=VerbosityLevel.MEDIUM,
                description="Medium verbosity",
            ),
            Option(
                name="vv",
                short_name="vv",
                is_flag=True,
                type=bool,
                value=VerbosityLevel.HIGH,
                description="High verbosity",
            ),
            Option(
                name="vvv",
                short_name="vvv",
                is_flag=True,
                type=bool,
                value=VerbosityLevel.MAXIMUM,
                description="Maximum verbosity",
            ),
            Option(
                name="output_format",
                short_name=False,
                type=str,
                value="str",
                description="The way to render the output",
            ),
            Option(
                name="output_target",
                short_name=False,
                type=str,
                value="str",
                description="The emplacement where placing the output (stdout, file, ...)",
                multiple=True,
                always_list=True,
            ),
            Option(
                name="indentation_level",
                short_name=False,
                is_flag=False,
                type=int,
                description="Number of indentation levels to use",
            ),
            Option(
                name="force_request_id",
                short_name=False,
                type=str,
                description="Force a specific request ID (used by external processes)",
            ),
            Option(
                name="subprocess",
                short_name=False,
                is_flag=True,
                type=bool,
                description="Indicate this process was launched as a subprocess by another wex process",
            ),
            Option(
                name="ignore_missing_command",
                short_name=False,
                is_flag=True,
                type=bool,
                description="Exit silently with code 0 if the command is not found",
            ),
        ]

    def _get_live_command_registry_entries(self) -> list[dict]:
        return list(self._registry.get_all_commands().values())

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

    def _init_command_line_core_args(self) -> None:
        from wexample_helpers.helpers.array import array_unique

        super()._init_command_line_core_args()

        self._config_arg_output_format = (
            self._config_arg_output_format or OUTPUT_FORMAT_STR
        )
        # By default, the kernel does not return data, but only display io messages.
        # The output should be explicitly asked to be returned in file or output.
        self._config_arg_output_target = array_unique(
            self._config_arg_output_target or [OUTPUT_TARGET_NONE]
        )

    def _init_command_line_kernel(self: AbstractKernel) -> None:
        super()._init_command_line_kernel()

        # CLI defaults to stdout output (programmatic use defaults to none)
        if not self._config_arg_output_target or self._config_arg_output_target == [
            OUTPUT_TARGET_NONE
        ]:
            from wexample_app.const.output import OUTPUT_TARGET_STDOUT

            self._config_arg_output_target = [OUTPUT_TARGET_STDOUT]

        # We can then use config.
        if self._config_arg_quiet:
            self.io.default_context_verbosity = VerbosityLevel.QUIET
            self.io.default_response_verbosity = VerbosityLevel.QUIET
        elif self._config_arg_v:
            self.io.default_context_verbosity = VerbosityLevel.DEFAULT
            self.io.default_response_verbosity = VerbosityLevel.DEFAULT
        elif self._config_arg_vv:
            self.io.default_context_verbosity = VerbosityLevel.HIGH
            self.io.default_response_verbosity = VerbosityLevel.HIGH
        elif self._config_arg_vvv:
            self.io.default_context_verbosity = VerbosityLevel.MAXIMUM
            self.io.default_response_verbosity = VerbosityLevel.MAXIMUM

        self.io.indentation = min(
            self._config_arg_indentation_level or self.io.indentation,
            int(self.io.terminal_width / 3),
        )

    def _init_local_env(self) -> None:
        """Load .wex/local/env.yml into os.environ and env_config.

        This file is per-machine, gitignored. Use it to declare env vars that
        subprocesses (e.g. git over SSH) need but that cannot be committed.
        Example: SSH_AUTH_SOCK: /run/user/1000/keyring/ssh
        """
        import os

        local_env = self.workdir.get_local_data("env")
        if not local_env:
            return

        self.env_config.update(local_env)
        os.environ.update({k: v for k, v in local_env.items() if v is not None})

    def _init_logging(self) -> None:
        import sys

        from wexample_wex_core.const.globals import CORE_COMMAND_NAME

        level = logging.WARNING
        logger = logging.getLogger(str(CORE_COMMAND_NAME))
        logger.setLevel(level)

        if not logger.handlers:
            handler = logging.StreamHandler(sys.stderr)
            handler.setLevel(level)
            handler.setFormatter(
                logging.Formatter("%(name)s %(levelname)s: %(message)s")
            )
            logger.addHandler(handler)

        self._logger = logger

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

        # Live resolvers (app, user) are never persisted — always scan fresh.
        for resolver in self.get_resolvers().values():
            if resolver.is_live():
                self._registry.update_resolver(
                    resolver.get_snake_short_class_name(),
                    resolver.build_registry_data(),
                )

    def _init_script_runner_registry(self) -> None:
        from wexample_wex_core.yaml.script_runner_registry import ScriptRunnerRegistry

        self._script_runner_registry = ScriptRunnerRegistry()

    def _init_step_guard_registry(self) -> None:
        from wexample_wex_core.common.abstract_addon_manager import AbstractAddonManager
        from wexample_wex_core.yaml.step_guard_registry import StepGuardRegistry

        registry = StepGuardRegistry()
        for addon in self.get_addons().values():
            for guard_class in cast(
                AbstractAddonManager, addon
            ).get_step_guard_classes():
                registry.register(guard_class())
        self._step_guard_registry = registry
