from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from wexample_app.runner.yaml_command_runner import YamlCommandRunner

if TYPE_CHECKING:
    from wexample_app.common.command import Command

    from wexample_wex_core.common.command_request import CommandRequest
    from wexample_wex_core.common.kernel import Kernel
    from wexample_wex_core.yaml.yaml_command_definition import YamlCommandDefinition


class CoreYamlCommandRunner(YamlCommandRunner):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        # Instance-level cache: avoid re-reading YAML on every execution,
        # but don't share state across runner instances (e.g. between tests).
        self._definition_cache: dict[Path, YamlCommandDefinition] = {}

    # ------------------------------------------------------------------
    # Variable management
    # ------------------------------------------------------------------
    @staticmethod
    def _build_variables(
        kwargs: dict, yaml_path: Path, kernel: Kernel
    ) -> dict[str, str]:
        import os

        from wexample_app.workdir.mixin.with_setup_env_parameter_mixin import (
            WithSetupEnvParameterMixin,
        )

        # Lowest priority: .wex/local/env.yml from the call workdir (where wex was invoked)
        variables: dict[str, str] = (
            WithSetupEnvParameterMixin.get_env_parameters_from_path(
                kernel.call_workdir.get_path()
            ).to_dict()
        )

        # Override with process environment variables
        variables.update(os.environ)
        # Built-ins override env
        variables["PATH_CURRENT"] = str(yaml_path.parent)
        # Option values have highest priority
        for key, value in kwargs.items():
            if key != "context" and value is not None:
                variables[key.upper()] = str(value)
        return variables

    @staticmethod
    def _capture_variable(
        response: Any, variable_name: str, variables: dict[str, str]
    ) -> None:
        from wexample_app.const.output import OUTPUT_FORMAT_STR
        from wexample_app.response.shell_command_response import ShellCommandResponse

        if isinstance(response, ShellCommandResponse):
            variables[variable_name.upper()] = response.get_formatted(OUTPUT_FORMAT_STR)

    # ------------------------------------------------------------------
    # Response collection
    # ------------------------------------------------------------------
    @staticmethod
    def _collect_responses(responses: list, kernel: Kernel) -> Any:
        if not responses:
            return None
        if len(responses) == 1:
            return responses[0]

        from wexample_app.response.response_collection_response import (
            ResponseCollectionResponse,
        )

        return ResponseCollectionResponse(kernel=kernel, content=responses)

    @staticmethod
    def _execute_internal_command(
        step: dict, variables: dict[str, str], kernel: Kernel
    ) -> Any:
        from wexample_app.const.output import OUTPUT_TARGET_NONE

        from wexample_wex_core.common.command_request import CommandRequest

        # step is already fully substituted at this point
        args = step.get("args", {})
        sub_request = CommandRequest(
            kernel=kernel,
            name=step["command"],
            arguments=args if isinstance(args, dict) else {},
            output_target=[OUTPUT_TARGET_NONE],
        )
        return kernel.execute_kernel_command(sub_request)

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    @staticmethod
    def _validate_step_keys(step: dict, runner, kernel: Kernel) -> None:
        """Raise if the step contains keys not declared by the runner."""
        # Structural keys always valid — not runner-specific
        structural = {"runner", "variable"}
        valid = (
            structural
            | set(runner.get_step_options())
            | set(kernel.step_guard_registry.get_all_step_options())
        )
        unknown = set(step.keys()) - valid

        if unknown:
            raise ValueError(
                f"Unknown option(s) {sorted(unknown)} for runner '{runner.get_runner_name()}'. "
                f"Valid options: {sorted(valid - structural)}"
            )

    def build_runnable_command(self, request: CommandRequest) -> Command | None:
        from wexample_wex_core.command.extended_command import ExtendedCommand
        from wexample_wex_core.yaml.yaml_command_definition import YamlCommandDefinition

        path = self.build_command_path(request)
        if path is None or not path.exists():
            return None

        if path not in self._definition_cache:
            self._definition_cache[path] = YamlCommandDefinition.from_path(path)

        definition = self._definition_cache[path]
        wrapper = self._build_wrapper(definition)
        return ExtendedCommand(kernel=self.kernel, command_wrapper=wrapper)

    def will_run(self, request: CommandRequest) -> bool:
        import os.path

        path = self.build_command_path(request=request)
        if path is None:
            return False
        if os.path.exists(path):
            return True
        # Catch the common mistake of naming the YAML file with underscores
        path.parent / f"{path.stem.replace('-', '_')}{path.suffix}"
        kebab_path = path.parent / f"{path.stem.replace('_', '-')}{path.suffix}"
        if kebab_path.exists():
            from wexample_app.exception.app_runtime_exception import AppRuntimeException

            raise AppRuntimeException(
                f"Command file uses hyphens in its name: '{kebab_path.name}'. "
                f"Rename to: '{path.name}'"
            )
        return False

    # ------------------------------------------------------------------
    # Wrapper construction
    # ------------------------------------------------------------------
    def _build_wrapper(self, definition: YamlCommandDefinition) -> CommandMethodWrapper:
        from wexample_wex_core.common.command_method_wrapper import CommandMethodWrapper
        from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON

        return CommandMethodWrapper(
            function=self._make_executor(definition),
            description=definition.description,
            options=list(definition.options),
            aliases=list(definition.aliases),
            sudo=definition.sudo,
            webhook=definition.webhook,
            attachments={k: list(v) for k, v in definition.attachments.items()},
            type=COMMAND_TYPE_ADDON,
        )

    # ------------------------------------------------------------------
    # Step execution
    # ------------------------------------------------------------------
    def _execute_step(
        self, step: dict, variables: dict[str, str], kernel: Kernel
    ) -> tuple[Any, str | None]:
        """Return (response, capture_variable_name)."""
        # Bare string step → implicit bash
        if isinstance(step, str):
            step = {"runner": "bash", "script": step}

        capture_var: str | None = step.get("variable")

        name: str | None = step.get("name")
        if name:
            kernel.io.log(name)

        if kernel.step_guard_registry.should_skip_step(step, kernel):
            kernel.io.log("Step skipped by guard.")
            return None, None

        if "command" in step:
            return self._execute_internal_command(step, variables, kernel), capture_var

        runner_name = (
            step.get("runner", "bash")
            if ("script" in step or "file" in step)
            else step.get("runner")
        )
        if runner_name:
            runner = kernel.script_runner_registry.get(runner_name)
            if runner is None:
                raise ValueError(
                    f"Unknown YAML script runner: '{runner_name}'. "
                    f"Available: {list(kernel.script_runner_registry.all().keys())}"
                )
            self._validate_step_keys(step, runner, kernel)
            return runner.run(step, variables, kernel), capture_var

        return None, None

    def _make_executor(self, definition: YamlCommandDefinition):
        """Return a callable that executes the YAML scripts."""
        kernel: Kernel = self.kernel
        scripts = definition.scripts
        yaml_path = definition.path

        def _execute(**kwargs: Any) -> Any:
            from wexample_wex_core.yaml.yaml_variable import yaml_substitute_step

            variables = self._build_variables(kwargs, yaml_path, kernel)
            responses = []

            for step in [yaml_substitute_step(s, variables) for s in scripts]:
                response, capture_var = self._execute_step(step, variables, kernel)

                if capture_var and response is not None:
                    self._capture_variable(response, capture_var, variables)
                    continue

                if response is not None:
                    responses.append(response)

            return self._collect_responses(responses, kernel)

        return _execute
