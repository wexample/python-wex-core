def test_ping_in_registry(kernel):
    addon_commands = kernel.get_configuration_registry().get_addon_commands()

    assert "default" in addon_commands
    assert "ping/pong" in addon_commands["default"]
