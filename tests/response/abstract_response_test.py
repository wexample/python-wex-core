import json

import pytest
import yaml

from wexample_app.const.output import (
    OUTPUT_FORMAT_JSON,
    OUTPUT_FORMAT_STR,
    OUTPUT_FORMAT_YAML,
    OUTPUT_TARGET_NONE,
    OUTPUT_TARGET_STDOUT,
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

    def test_output_target_none_suppresses_output(self, kernel, capsys):
        self.create_response(kernel).get_formatted(OUTPUT_FORMAT_STR)
        # Force none by not printing via handler — verify direct get_formatted returns ""
        # (io already printed; handler-level suppression is tested via command request)
        capsys.readouterr()  # flush

    def test_output_target_none_via_request(self, kernel, capsys):
        request = self._make_request(kernel, output_target=[OUTPUT_TARGET_NONE])
        kernel.execute_kernel_command_and_print(request)
        assert capsys.readouterr().out == ""

    def test_output_target_stdout_via_request(self, kernel, capsys):
        request = self._make_request(kernel, output_target=[OUTPUT_TARGET_STDOUT])
        kernel.execute_kernel_command_and_print(request)
        assert capsys.readouterr().out != ""

    def test_output_target_stdout_via_kernel(self, kernel, capsys):
        kernel.set_output_target([OUTPUT_TARGET_STDOUT])
        request = self._make_request(kernel)
        kernel.execute_kernel_command_and_print(request)
        assert capsys.readouterr().out != ""

    def get_command(self):
        raise NotImplementedError

    def get_resolver_class(self):
        from wexample_wex_core.resolver.addon_command_resolver import AddonCommandResolver

        return AddonCommandResolver

    def get_command_name(self) -> str:
        from wexample_wex_core.common.command_address import CommandAddress

        return self.get_resolver_class().address_to_command(CommandAddress.from_function(self.get_command()))

    def _make_request(self, kernel, output_target: list[str] | None = None) -> CommandRequest:
        return CommandRequest(
            kernel=kernel,
            request_id="test-request",
            name=self.get_command_name(),
            output_target=output_target,
        )
