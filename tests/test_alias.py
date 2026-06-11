from __future__ import annotations

from wexample_app.const.output import OUTPUT_TARGET_NONE
from wexample_app.response.default_response import DefaultResponse
from wexample_app.response.dict_response import DictResponse

from tests.abstract_kernel_test import AbstractKernelTest
from wexample_wex_core.common.command_request import CommandRequest


class TestAlias(AbstractKernelTest):
    def test_alias_in_registry(self, kernel) -> None:
        addon_commands = kernel.get_configuration_registry().get_addon_commands()
        cmd_data = addon_commands["demo"]["ping/pong"]
        assert "ping" in cmd_data["alias"]

    def test_alias_resolves_to_canonical(self, kernel) -> None:
        """Calling 'ping' (alias) executes demo::ping/pong."""
        request = CommandRequest(
            kernel=kernel,
            name="ping",
            output_target=[OUTPUT_TARGET_NONE],
            arguments={"type": "dict"},
        )
        response = kernel.execute_kernel_command(request)
        assert isinstance(response, DictResponse)
        assert response.content == {"status": "pong"}

    def test_hi_alias_in_registry(self, kernel) -> None:
        addon_commands = kernel.get_configuration_registry().get_addon_commands()
        cmd_data = addon_commands["core"]["ping/hi"]
        assert "hi" in cmd_data["alias"]

    def test_hi_alias_resolves(self, kernel) -> None:
        """Calling 'hi' (short alias) executes default::check/hi."""
        request = CommandRequest(
            kernel=kernel,
            name="hi",
            output_target=[OUTPUT_TARGET_NONE],
        )
        response = kernel.execute_kernel_command(request)
        assert isinstance(response, DefaultResponse)
        assert response.content == "hi!"
