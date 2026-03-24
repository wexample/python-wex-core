from wexample_app.const.output import OUTPUT_TARGET_NONE
from wexample_app.response.null_response import NullResponse


def test_ping_in_registry(kernel):
    addon_commands = kernel.get_configuration_registry().get_addon_commands()

    assert "default" in addon_commands
    assert "ping/pong" in addon_commands["default"]


def test_ping_executes(kernel):
    from wexample_wex_core.common.command_request import CommandRequest

    request = CommandRequest(
        kernel=kernel,
        request_id="test-ping",
        name="default::ping/pong",
        output_target=[OUTPUT_TARGET_NONE],
    )

    response = kernel.execute_kernel_command(request)

    assert isinstance(response, NullResponse)
