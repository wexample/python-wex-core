import json

from wexample_app.const.output import OUTPUT_FORMAT_JSON, OUTPUT_FORMAT_STR, OUTPUT_TARGET_NONE
from wexample_app.response.dict_response import DictResponse
from wexample_app.response.list_response import ListResponse
from wexample_wex_core.response.response_collection_response import ResponseCollectionResponse

from tests.response.abstract_response_test import AbstractResponseTest


class TestResponseCollectionResponse(AbstractResponseTest):
    def create_response(self, kernel) -> ResponseCollectionResponse:
        return ResponseCollectionResponse(
            kernel=kernel,
            content=[
                DictResponse(kernel=kernel, content={"color": "red"}),
                ListResponse(kernel=kernel, content=["a", "b", "c"]),
            ],
        )

    def get_command(self):
        from wexample_wex_core.addons.demo.commands.ping.pong import demo__ping__pong

        return demo__ping__pong

    def get_command_arguments(self) -> dict:
        return {"type": "collection"}

    def test_str_renders_all_items(self, kernel, capsys):
        self.create_response(kernel).get_formatted(OUTPUT_FORMAT_STR)
        out = capsys.readouterr().out

        assert "color" in out
        assert "red" in out
        assert "a" in out
        assert "b" in out

    def test_json_contains_all_items(self, kernel):
        output = self.create_response(kernel).get_formatted(OUTPUT_FORMAT_JSON)
        data = json.loads(output)

        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0] == {"color": "red"}
        assert data[1] == ["a", "b", "c"]

    def test_ping_returns_collection_response(self, kernel):
        response = kernel.execute_kernel_command(self._make_request(kernel, output_target=[OUTPUT_TARGET_NONE]))
        assert isinstance(response, ResponseCollectionResponse)

    def test_ping_collection_contains_two_items(self, kernel):
        response = kernel.execute_kernel_command(self._make_request(kernel, output_target=[OUTPUT_TARGET_NONE]))
        assert len(response.content) == 2
        assert isinstance(response.content[0], DictResponse)
        assert isinstance(response.content[1], ListResponse)
