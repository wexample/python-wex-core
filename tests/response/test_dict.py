import json

from wexample_app.const.output import OUTPUT_FORMAT_JSON, OUTPUT_FORMAT_STR, OUTPUT_TARGET_NONE, OUTPUT_TARGET_STDOUT
from wexample_wex_core.common.command_request import CommandRequest
from wexample_wex_core.response.dict_response import DictResponse


def test_dict_response_str(kernel, capsys):
    response = DictResponse(kernel=kernel, content={"status": "pong", "version": "6"})
    response.get_formatted(OUTPUT_FORMAT_STR)
    out = capsys.readouterr().out

    assert "status" in out
    assert "pong" in out
    assert "version" in out
    assert "6" in out


def test_dict_response_str_with_title(kernel, capsys):
    response = DictResponse(kernel=kernel, content={"a": "1"}, title="My title")
    response.get_formatted(OUTPUT_FORMAT_STR)
    out = capsys.readouterr().out

    assert "My title" in out
    assert "a" in out
    assert "1" in out


def test_dict_response_json(kernel):
    response = DictResponse(kernel=kernel, content={"status": "pong", "version": "6"})
    output = response.get_formatted(OUTPUT_FORMAT_JSON)
    data = json.loads(output)

    assert data == {"status": "pong", "version": "6"}


def test_ping_returns_dict_response(kernel):
    request = CommandRequest(
        kernel=kernel,
        request_id="test-ping",
        name="default::ping/pong",
        output_target=[OUTPUT_TARGET_NONE],
    )
    response = kernel.execute_kernel_command(request)

    assert isinstance(response, DictResponse)
    assert response.content == {"status": "pong"}


def test_output_target_none_suppresses_output(kernel, capsys):
    request = CommandRequest(
        kernel=kernel,
        request_id="test-none",
        name="default::ping/pong",
        output_target=[OUTPUT_TARGET_NONE],
    )
    kernel.execute_kernel_command_and_print(request)

    assert capsys.readouterr().out == ""


def test_output_target_stdout_prints_output(kernel_stdout, capsys):
    request = CommandRequest(
        kernel=kernel_stdout,
        request_id="test-stdout",
        name="default::ping/pong",
        output_target=[OUTPUT_TARGET_STDOUT],
    )
    kernel_stdout.execute_kernel_command_and_print(request)

    out = capsys.readouterr().out
    assert "status" in out and "pong" in out
