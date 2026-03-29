from tests.abstract_kernel_test import AbstractKernelTest
from wexample_wex_core.addons.demo.commands.sudo.check import demo__sudo__check
from wexample_wex_core.resolver.abstract_command_resolver import AbstractCommandResolver


class TestAsSudo(AbstractKernelTest):
    def test_sudo_flag_in_registry(self, kernel):
        addon_commands = kernel.get_configuration_registry().get_addon_commands()
        cmd_data = addon_commands["demo"]["sudo/check"]
        assert cmd_data["sudo"] is True

    def test_non_sudo_command_has_no_flag(self, kernel):
        addon_commands = kernel.get_configuration_registry().get_addon_commands()
        cmd_data = addon_commands["demo"]["ping/pong"]
        assert cmd_data.get("sudo") is False

    def test_sudo_wrapper_flag(self):
        assert demo__sudo__check.sudo is True
