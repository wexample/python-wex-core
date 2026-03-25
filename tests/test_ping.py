from wexample_app.const.output import OUTPUT_TARGET_NONE
from wexample_wex_core.common.command_request import CommandRequest
from wexample_wex_core.response.dict_response import DictResponse

from tests.abstract_kernel_test import AbstractKernelTest


class TestPing(AbstractKernelTest):
    def test_ping_in_registry(self, kernel):
        addon_commands = kernel.get_configuration_registry().get_addon_commands()

        assert "default" in addon_commands
        assert "ping/pong" in addon_commands["default"]

    # TODO: move to wex-core/src/wexample_wex_core/addons/default/commands/ping/test_pong.py
    #       and register as the official test for default::ping/pong in the registry (RegistryCommandData.test)
    def test_ping_executes(self, kernel):
        request = CommandRequest(
            kernel=kernel,
            request_id="test-ping",
            name="default::ping/pong",
            output_target=[OUTPUT_TARGET_NONE],
            arguments={"type": "dict"},
        )

        response = kernel.execute_kernel_command(request)

        assert isinstance(response, DictResponse)
