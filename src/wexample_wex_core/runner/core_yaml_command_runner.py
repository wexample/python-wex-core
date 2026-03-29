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
    # Cache parsed definitions: avoid re-reading YAML on every execution.
    _definition_cache: dict[Path, YamlCommandDefinition] = {}

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

    # ------------------------------------------------------------------
    # Wrapper construction
    # ------------------------------------------------------------------

    def _build_wrapper(self, definition: YamlCommandDefinition):
        from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON
        from wexample_wex_core.common.command_method_wrapper import CommandMethodWrapper

        return CommandMethodWrapper(
            function=self._make_executor(definition),
            description=definition.description,
            options=list(definition.options),
            aliases=list(definition.aliases),
            sudo=definition.sudo,
            attachments={k: list(v) for k, v in definition.attachments.items()},
            type=COMMAND_TYPE_ADDON,
        )

    def _make_executor(self, definition: YamlCommandDefinition):
        """Return a callable that executes the YAML scripts."""
        kernel: Kernel = self.kernel
        scripts = definition.scripts
        yaml_path = definition.path

        def _execute(**kwargs: Any) -> Any:
            variables = self._build_variables(kwargs, yaml_path)
            responses = []

            for step in scripts:
                response, capture_var = self._execute_step(step, variables, kernel)

                if capture_var and response is not None:
                    self._capture_variable(response, capture_var, variables)
                    continue

                if response is not None:
                    responses.append(response)

            return self._collect_responses(responses, kernel)

        return _execute

    # ------------------------------------------------------------------
    # Variable management
    # ------------------------------------------------------------------

    @staticmethod
    def _build_variables(kwargs: dict, yaml_path: Path) -> dict[str, str]:
        import os

        # Lower priority: environment variables
        variables: dict[str, str] = {k: v for k, v in os.environ.items()}
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
    # Step execution
    # ------------------------------------------------------------------

    def _execute_step(
        self, step: dict, variables: dict[str, str], kernel: Kernel
    ) -> tuple[Any, str | None]:
        """Return (response, capture_variable_name)."""
        capture_var: str | None = step.get("variable")

        if "command" in step:
            return self._execute_internal_command(step, variables, kernel), capture_var

        runner_name = step.get("runner")
        if runner_name:
            runner = kernel.script_runner_registry.get(runner_name)
            if runner is None:
                raise ValueError(
                    f"Unknown YAML script runner: '{runner_name}'. "
                    f"Available: {list(kernel.script_runner_registry.all().keys())}"
                )
            return runner.run(step, variables, kernel), capture_var

        return None, None

    @staticmethod
    def _execute_internal_command(
        step: dict, variables: dict[str, str], kernel: Kernel
    ) -> Any:
        from wexample_app.const.output import OUTPUT_TARGET_NONE
        from wexample_wex_core.common.command_request import CommandRequest
        from wexample_wex_core.yaml.yaml_variable import yaml_substitute

        args = step.get("args", {})
        resolved_args = (
            {k: yaml_substitute(str(v), variables) for k, v in args.items()}
            if isinstance(args, dict)
            else {}
        )

        sub_request = CommandRequest(
            kernel=kernel,
            name=step["command"],
            arguments=resolved_args,
            output_target=[OUTPUT_TARGET_NONE],
        )
        return kernel.execute_kernel_command(sub_request)

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

        collection = ResponseCollectionResponse(kernel=kernel)
        for r in responses:
            collection.append(r)
        return collection
