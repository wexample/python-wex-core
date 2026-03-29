from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from wexample_app.runner.yaml_command_runner import YamlCommandRunner

if TYPE_CHECKING:
    from pathlib import Path

    from wexample_app.common.command import Command

    from wexample_wex_core.common.command_request import CommandRequest


class CoreYamlCommandRunner(YamlCommandRunner):
    def build_runnable_command(self, request: CommandRequest) -> Command | None:
        from wexample_wex_core.command.extended_command import ExtendedCommand

        wrapper = self._build_yaml_wrapper(request)
        if wrapper is None:
            return None

        return ExtendedCommand(kernel=self.kernel, command_wrapper=wrapper)

    def _build_yaml_wrapper(self, request: CommandRequest):
        import yaml

        from wexample_wex_core.common.command_method_wrapper import CommandMethodWrapper

        path = self.build_command_path(request)
        if path is None or not path.exists():
            return None

        with open(path) as f:
            data = yaml.safe_load(f) or {}

        description = data.get("description")
        options = self._parse_yaml_options(data.get("options", []))
        aliases, sudo, attachments = self._parse_yaml_decorators(data.get("decorators", []))
        scripts = data.get("scripts", [])

        function = self._build_script_function(scripts, path)

        from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON

        return CommandMethodWrapper(
            function=function,
            description=description,
            options=options,
            aliases=aliases,
            sudo=sudo,
            attachments=attachments,
            type=COMMAND_TYPE_ADDON,
        )

    def _parse_yaml_options(self, options_data: list) -> list:
        from wexample_app.command.option import Option

        options = []
        for opt in options_data:
            name = opt.get("name")
            if not name:
                continue

            type_str = opt.get("type", "str")
            type_map = {"str": str, "int": int, "float": float, "bool": bool}
            python_type = type_map.get(type_str, str)

            options.append(
                Option(
                    name=name,
                    type=python_type,
                    required=opt.get("required", False),
                    default=opt.get("default", None),
                    description=opt.get("help"),
                    short_name=opt.get("short"),
                    is_flag=opt.get("is_flag", False),
                    multiple=opt.get("multiple", False),
                )
            )

        return options

    def _parse_yaml_decorators(self, decorators: list) -> tuple[list, bool, dict]:
        aliases: list[str] = []
        sudo = False
        attachments: dict[str, list] = {"before": [], "after": []}

        for dec in decorators:
            dec_name = dec.get("name")
            dec_args = dec.get("args", {})

            if dec_name == "sudo":
                sudo = True
            elif dec_name == "alias":
                alias_value = dec_args if isinstance(dec_args, str) else str(dec_args)
                aliases.append(alias_value)
            elif dec_name == "attach":
                if isinstance(dec_args, dict):
                    position = dec_args.get("position", "after")
                    attachments[position].append(
                        {
                            "command": dec_args.get("command", ""),
                            "pass_args": dec_args.get("pass_args", False),
                        }
                    )

        return aliases, sudo, attachments

    def _build_script_function(self, scripts: list, yaml_path: Path):
        kernel = self.kernel

        def _run_scripts(**kwargs) -> Any:
            context = kwargs.get("context")
            variables: dict[str, str] = {}

            # Built-in variables
            variables["PATH_CURRENT"] = str(yaml_path.parent)

            # Option values from kwargs
            for key, value in kwargs.items():
                if key != "context" and value is not None:
                    variables[key.upper()] = str(value)

            responses = []

            for step in scripts:
                if "command" in step:
                    response = _run_internal_command(step, variables)
                elif "runner" in step:
                    response = _run_script_step(step, variables)
                else:
                    continue

                if response is not None:
                    # Capture output into variable if requested
                    capture_var = step.get("variable")
                    if capture_var:
                        from wexample_app.response.shell_command_response import (
                            ShellCommandResponse,
                        )

                        if isinstance(response, ShellCommandResponse):
                            from wexample_app.const.output import OUTPUT_FORMAT_STR

                            captured = response.get_formatted(OUTPUT_FORMAT_STR)
                            variables[capture_var.upper()] = captured
                        continue

                    responses.append(response)

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

        def _substitute(text: str, variables: dict) -> str:
            def replace_var(match):
                var_name = match.group(1)
                return variables.get(var_name, match.group(0))

            return re.sub(r"\$\{([^}]+)\}", replace_var, text)

        def _run_script_step(step: dict, variables: dict) -> Any:
            runner = step.get("runner", "bash")
            script = step.get("script")
            file = step.get("file")

            if runner == "bash":
                if script:
                    command = _substitute(script, variables)
                    from wexample_app.response.interactive_shell_command_response import (
                        InteractiveShellCommandResponse,
                    )

                    return InteractiveShellCommandResponse(
                        kernel=kernel, content=["bash", "-c", command]
                    )
                elif file:
                    file_path = _substitute(file, variables)
                    from wexample_app.response.interactive_shell_command_response import (
                        InteractiveShellCommandResponse,
                    )

                    return InteractiveShellCommandResponse(
                        kernel=kernel, content=["bash", file_path]
                    )

            elif runner == "python":
                if script:
                    code = _substitute(script, variables)
                    local_vars = {"kernel": kernel, **variables}
                    exec(code, {}, local_vars)  # noqa: S102
                    return None
                elif file:
                    file_path = _substitute(file, variables)
                    with open(file_path) as f:
                        code = f.read()
                    code = _substitute(code, variables)
                    local_vars = {"kernel": kernel, **variables}
                    exec(code, {}, local_vars)  # noqa: S102
                    return None

            return None

        def _run_internal_command(step: dict, variables: dict) -> Any:
            command_name = step.get("command")
            args = step.get("args", {})

            if isinstance(args, dict):
                resolved_args = {
                    k: _substitute(str(v), variables) for k, v in args.items()
                }
            else:
                resolved_args = {}

            from wexample_app.const.output import OUTPUT_TARGET_NONE
            from wexample_wex_core.common.command_request import CommandRequest

            sub_request = CommandRequest(
                kernel=kernel,
                name=command_name,
                arguments=resolved_args,
                output_target=[OUTPUT_TARGET_NONE],
            )
            return kernel.execute_kernel_command(sub_request)

        return _run_scripts
