from __future__ import annotations

from wexample_app.const.output import OUTPUT_TARGET_NONE
from wexample_app.response.dict_response import DictResponse

from tests.abstract_kernel_test import AbstractKernelTest
from wexample_wex_core.common.command_request import CommandRequest


class TestPing(AbstractKernelTest):
    # TODO: move to wex-core/src/wexample_wex_core.addons.demo.commands/ping/test_pong.py
    #       and register as the official test for demo::ping/pong in the registry (RegistryCommandData.test)
    def test_ping_executes(self, kernel) -> None:
        request = CommandRequest(
            kernel=kernel,
            name="demo::ping/pong",
            output_target=[OUTPUT_TARGET_NONE],
            arguments={"type": "dict"},
        )

        response = kernel.execute_kernel_command(request)

        assert isinstance(response, DictResponse)

    def test_ping_in_registry(self, kernel) -> None:
        addon_commands = kernel.get_configuration_registry().get_addon_commands()

        assert "demo" in addon_commands
        assert "ping/pong" in addon_commands["demo"]
