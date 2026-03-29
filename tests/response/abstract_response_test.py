import json

import pytest
import yaml

from wexample_app.const.output import (
    OUTPUT_FORMAT_JSON,
    OUTPUT_FORMAT_STR,
    OUTPUT_FORMAT_YAML,
    OUTPUT_TARGET_NONE,
)
from wexample_app.response.abstract_response import AbstractResponse
from wexample_wex_core.common.command_request import CommandRequest

from tests.abstract_kernel_test import AbstractKernelTest


class AbstractResponseTest(AbstractKernelTest):
    def create_response(self, kernel) -> AbstractResponse:
        raise NotImplementedError

    def test_str_format_renders(self, kernel, capsys):
        self.create_response(kernel).get_formatted(OUTPUT_FORMAT_STR)
        out = capsys.readouterr().out
        assert out is not None

    def test_json_format_is_valid(self, kernel):
        output = self.create_response(kernel).get_formatted(OUTPUT_FORMAT_JSON)
        assert json.loads(output) is not None

    def test_yaml_format_is_valid(self, kernel):
        output = self.create_response(kernel).get_formatted(OUTPUT_FORMAT_YAML)
        assert yaml.safe_load(output) is not None

    def get_command(self):
        raise NotImplementedError

    def get_resolver_class(self):
        from wexample_wex_core.resolver.addon_command_resolver import AddonCommandResolver

        return AddonCommandResolver

    def get_command_name(self) -> str:
        from wexample_wex_core.common.command_address import CommandAddress

        return self.get_resolver_class().address_to_command(CommandAddress.from_function(self.get_command()))

    def get_command_arguments(self) -> dict:
        return {}

    def _make_request(self, kernel, output_target: list[str] | None = None, arguments: dict | list | None = None, output_format: str | None = None) -> CommandRequest:
        return CommandRequest(
            kernel=kernel,
            name=self.get_command_name(),
            output_target=output_target,
            output_format=output_format,
            arguments=arguments if arguments is not None else self.get_command_arguments(),
        )
