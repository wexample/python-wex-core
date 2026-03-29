import json

from wexample_app.const.output import OUTPUT_FORMAT_JSON, OUTPUT_FORMAT_STR, OUTPUT_TARGET_NONE
from wexample_app.response.dict_response import DictResponse
from wexample_app.response.function_response import FunctionResponse

from tests.abstract_kernel_test import AbstractKernelTest
from wexample_wex_core.addons.demo.commands.ping.pong import PING_TYPE_FUNCTION, demo__ping__pong
from wexample_wex_core.resolver.abstract_command_resolver import AbstractCommandResolver


class TestFunctionResponse(AbstractKernelTest):
    def _make_dict_response(self, kernel) -> FunctionResponse:
        return FunctionResponse(
            kernel=kernel,
            content=lambda: DictResponse(kernel=kernel, content={"status": "pong"}),
        )

    def test_executes_callable(self, kernel):
        response = self._make_dict_response(kernel)
        assert isinstance(response._get_inner_response(), DictResponse)

    def test_str_format(self, kernel):
        output = self._make_dict_response(kernel).get_formatted(OUTPUT_FORMAT_STR)
        assert output is not None

    def test_json_format(self, kernel):
        output = self._make_dict_response(kernel).get_formatted(OUTPUT_FORMAT_JSON)
        assert json.loads(output) == {"status": "pong"}

    def test_cached_execution(self, kernel):
        call_count = 0

        def counted():
            nonlocal call_count
            call_count += 1
            return DictResponse(kernel=kernel, content={"status": "pong"})

        response = FunctionResponse(kernel=kernel, content=counted)
        response.get_formatted(OUTPUT_FORMAT_STR)
        response.get_formatted(OUTPUT_FORMAT_JSON)
        assert call_count == 1

    def test_via_ping_command(self, kernel):
        from wexample_wex_core.common.command_request import CommandRequest

        request = CommandRequest(
            kernel=kernel,
            name=AbstractCommandResolver.build_command_from_function(demo__ping__pong),
            output_target=[OUTPUT_TARGET_NONE],
            arguments={"type": PING_TYPE_FUNCTION},
        )
        response = kernel.execute_kernel_command(request)
        assert isinstance(response, FunctionResponse)
        assert isinstance(response._get_inner_response(), DictResponse)
