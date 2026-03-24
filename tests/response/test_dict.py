import json

from wexample_app.const.output import OUTPUT_FORMAT_JSON, OUTPUT_FORMAT_STR, OUTPUT_TARGET_NONE
from wexample_wex_core.response.dict_response import DictResponse


def test_dict_response_str(kernel):
    response = DictResponse(kernel=kernel, content={"status": "pong", "version": "6"})
    output = response.get_formatted(OUTPUT_FORMAT_STR)

    assert "status: pong" in output
    assert "version: 6" in output


def test_dict_response_str_with_title(kernel):
    response = DictResponse(kernel=kernel, content={"a": "1"}, title="My title")
    output = response.get_formatted(OUTPUT_FORMAT_STR)

    assert output.startswith("My title")
    assert "a: 1" in output


def test_dict_response_json(kernel):
    response = DictResponse(kernel=kernel, content={"status": "pong", "version": "6"})
    output = response.get_formatted(OUTPUT_FORMAT_JSON)
    data = json.loads(output)

    assert data == {"status": "pong", "version": "6"}


def test_ping_returns_dict_response(kernel):
    from wexample_wex_core.common.command_request import CommandRequest

    request = CommandRequest(
        kernel=kernel,
        request_id="test-ping",
        name="default::ping/pong",
        output_target=[OUTPUT_TARGET_NONE],
    )
    response = kernel.execute_kernel_command(request)

    assert isinstance(response, DictResponse)
    assert response.content == {"status": "pong"}
