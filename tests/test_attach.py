from wexample_app.const.output import OUTPUT_TARGET_NONE
from wexample_wex_core.common.command_request import CommandRequest

from tests.abstract_kernel_test import AbstractKernelTest


class TestAttach(AbstractKernelTest):
    def test_attachment_in_registry(self, kernel):
        addon_commands = kernel.get_configuration_registry().get_addon_commands()
        cmd_data = addon_commands["demo"]["hook/after-ping"]
        attachments_after = cmd_data["attachments"]["after"]
        assert any(a["command"] == "demo::ping/pong" for a in attachments_after)

    def test_after_hook_runs(self, kernel):
        """Executing demo::ping/pong should trigger demo::hook/after-ping."""
        import wexample_wex_core.addons.demo.commands.hook.after_ping as hook_mod

        hook_mod._HOOK_CALLED.clear()

        request = CommandRequest(
            kernel=kernel,
            request_id="test-attach",
            name="demo::ping/pong",
            output_target=[OUTPUT_TARGET_NONE],
            arguments={"type": "dict"},
        )
        kernel.execute_kernel_command(request)

        assert "after_ping" in hook_mod._HOOK_CALLED
