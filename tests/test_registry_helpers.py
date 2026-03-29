from tests.abstract_kernel_test import AbstractKernelTest


class TestRegistryHelpers(AbstractKernelTest):
    def test_get_all_commands_returns_flat_dict(self, kernel):
        commands = kernel.get_configuration_registry().get_all_commands()
        assert isinstance(commands, dict)
        assert len(commands) > 0
        assert all("command" in data for data in commands.values())

    def test_get_all_commands_keyed_by_command_name(self, kernel):
        commands = kernel.get_configuration_registry().get_all_commands()
        assert "demo::ping/pong" in commands
        assert commands["demo::ping/pong"]["command"] == "demo::ping/pong"

    def test_get_all_command_names_includes_aliases(self, kernel):
        names = kernel.get_configuration_registry().get_all_command_names()
        assert "demo::ping/pong" in names
        assert "ping" in names  # alias

    def test_get_sudo_commands(self, kernel):
        sudo_commands = kernel.get_configuration_registry().get_sudo_commands()
        assert "demo::sudo/check" in sudo_commands
        assert sudo_commands["demo::sudo/check"]["sudo"] is True

    def test_get_sudo_commands_excludes_non_sudo(self, kernel):
        sudo_commands = kernel.get_configuration_registry().get_sudo_commands()
        assert "demo::ping/pong" not in sudo_commands

    def test_find_command_by_name(self, kernel):
        cmd = kernel.get_configuration_registry().find_command("demo::ping/pong")
        assert cmd is not None
        assert cmd["command"] == "demo::ping/pong"

    def test_find_command_by_alias(self, kernel):
        cmd = kernel.get_configuration_registry().find_command("ping")
        assert cmd is not None
        assert cmd["command"] == "demo::ping/pong"

    def test_find_command_unknown_returns_none(self, kernel):
        assert kernel.get_configuration_registry().find_command("does::not/exist") is None

    def test_suggest_by_prefix(self, kernel):
        results = kernel.get_configuration_registry().suggest("demo::")
        assert "demo::ping/pong" in results
        assert "demo::sudo/check" in results
        assert all(r.startswith("demo::") for r in results)

    def test_suggest_alias_by_prefix(self, kernel):
        results = kernel.get_configuration_registry().suggest("pi")
        assert "ping" in results
