from wexample_app.const.output import OUTPUT_TARGET_NONE
from wexample_wex_core.common.command_request import CommandRequest

from tests.abstract_kernel_test import AbstractKernelTest


class TestAttach(AbstractKernelTest):
    def test_attachment_in_registry(self, kernel):
        addon_commands = kernel.get_configuration_registry().get_addon_commands()
        cmd_data = addon_commands["demo"]["hook/after_ping"]
        attachments_after = cmd_data["attachments"]["after"]
        assert any(a["command"] == "demo::ping/pong" for a in attachments_after)

    def test_after_hook_runs(self, kernel):
        """Executing demo::ping/pong should trigger demo::hook/after_ping."""
        kernel._test_after_ping_ran = False

        request = CommandRequest(
            kernel=kernel,
            name="demo::ping/pong",
            output_target=[OUTPUT_TARGET_NONE],
            arguments={"type": "dict"},
        )
        kernel.execute_kernel_command(request)

        assert kernel._test_after_ping_ran is True
