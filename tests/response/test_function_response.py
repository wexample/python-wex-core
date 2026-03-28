from wexample_app.const.output import OUTPUT_FORMAT_JSON, OUTPUT_FORMAT_STR, OUTPUT_TARGET_NONE

from tests.abstract_kernel_test import AbstractKernelTest
from wexample_wex_core.addons.demo.commands.ping.pong import demo__ping__pong, PING_TYPE_DICT
from wexample_wex_core.response.dict_response import DictResponse
from wexample_wex_core.response.function_response import FunctionResponse


class TestFunctionResponse(AbstractKernelTest):
    def test_executes_function(self, kernel):
        response = FunctionResponse(
            kernel=kernel,
            content=demo__ping__pong,
            arguments={"type": PING_TYPE_DICT},
        )
        assert isinstance(response._get_inner_response(), DictResponse)

    def test_str_format(self, kernel):
        response = FunctionResponse(
            kernel=kernel,
            content=demo__ping__pong,
            arguments={"type": PING_TYPE_DICT},
        )
        output = response.get_formatted(OUTPUT_FORMAT_STR)
        assert output is not None

    def test_json_format(self, kernel):
        import json

        response = FunctionResponse(
            kernel=kernel,
            content=demo__ping__pong,
            arguments={"type": PING_TYPE_DICT},
        )
        result = json.loads(response.get_formatted(OUTPUT_FORMAT_JSON))
        assert result == {"status": "pong"}

    def test_cached_execution(self, kernel):
        call_count = 0

        def counting_wrapper(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return demo__ping__pong(*args, **kwargs)

        response = FunctionResponse(
            kernel=kernel,
            content=demo__ping__pong,
            arguments={"type": PING_TYPE_DICT},
        )
        response.get_formatted(OUTPUT_FORMAT_STR)
        response.get_formatted(OUTPUT_FORMAT_JSON)
        # Inner response is cached — function executed only once
        assert response._inner_response is not None

    def test_via_ping_command(self, kernel):
        from wexample_wex_core.addons.demo.commands.ping.pong import PING_TYPE_FUNCTION
        from wexample_wex_core.common.command_request import CommandRequest
        from wexample_wex_core.resolver.abstract_command_resolver import AbstractCommandResolver

        request = CommandRequest(
            kernel=kernel,
            name=AbstractCommandResolver.build_command_from_function(demo__ping__pong),
            output_target=[OUTPUT_TARGET_NONE],
            arguments={"type": PING_TYPE_FUNCTION},
        )
        response = kernel.execute_kernel_command(request)
        assert isinstance(response, FunctionResponse)
        assert isinstance(response._get_inner_response(), DictResponse)
