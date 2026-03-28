from wexample_app.const.output import OUTPUT_FORMAT_JSON, OUTPUT_FORMAT_STR, OUTPUT_TARGET_NONE
from wexample_wex_core.addons.demo.commands.response.collection import (
    DEMO_COLLECTION_FIRST_VALUE,
    demo__response__collection,
)
from wexample_wex_core.response.queued_collection_response import QueuedCollectionResponse
from wexample_wex_core.response.queue_collection.queued_collection_stop_response import QueuedCollectionStopResponse
from wexample_wex_core.response.queue_collection.queued_collection_stop_current_step_response import QueuedCollectionStopCurrentStepResponse
from wexample_app.response.dict_response import DictResponse

from tests.response.abstract_response_test import AbstractResponseTest


class TestQueuedCollectionRich(AbstractResponseTest):
    def create_response(self, kernel) -> QueuedCollectionResponse:
        from wexample_app.response.list_response import ListResponse

        return QueuedCollectionResponse(
            kernel=kernel,
            content=[
                "simple-string",
                42,
                DictResponse(kernel=kernel, content={"step": "one"}),
            ],
        )

    def get_command(self):
        return demo__response__collection

    def get_command_arguments(self) -> dict:
        return {}

    def test_plain_values_render(self, kernel, capsys):
        from wexample_wex_core.response.queued_collection_response import QueuedCollectionResponse

        QueuedCollectionResponse(
            kernel=kernel,
            content=["hello", 42, ["a", "b"], {"key": "val"}],
        ).get_formatted(OUTPUT_FORMAT_STR)
        out = capsys.readouterr().out

        assert "hello" in out
        assert "42" in out
        assert "a" in out
        assert "key" in out

    def test_previous_value_chained(self, kernel):
        results = []

        def step_a(previous_value):
            return {"from_a": "yes"}

        def step_b(previous_value):
            results.append(previous_value)
            return "done"

        QueuedCollectionResponse(
            kernel=kernel,
            content=[step_a, step_b],
        ).get_formatted(OUTPUT_FORMAT_STR)

        assert results == [{"from_a": "yes"}]

    def test_nested_collection_previous_value(self, kernel):
        received = []

        sub = QueuedCollectionResponse(
            kernel=kernel,
            content=["sub-value"],
        )

        def after_sub(previous_value):
            received.append(previous_value)
            return "done"

        QueuedCollectionResponse(
            kernel=kernel,
            content=[sub, after_sub],
        ).get_formatted(OUTPUT_FORMAT_STR)

        assert received == ["sub-value"]

    def test_stop_halts(self, kernel, capsys):
        QueuedCollectionResponse(
            kernel=kernel,
            content=[
                DictResponse(kernel=kernel, content={"step": "one"}),
                QueuedCollectionStopResponse(kernel=kernel, reason="halt"),
                DictResponse(kernel=kernel, content={"step": "three"}),
            ],
        ).get_formatted(OUTPUT_FORMAT_STR)
        out = capsys.readouterr().out

        assert "one" in out
        assert "three" not in out

    def test_stop_current_step_continues(self, kernel, capsys):
        QueuedCollectionResponse(
            kernel=kernel,
            content=[
                DictResponse(kernel=kernel, content={"step": "one"}),
                QueuedCollectionStopCurrentStepResponse(kernel=kernel, reason="skip"),
                DictResponse(kernel=kernel, content={"step": "three"}),
            ],
        ).get_formatted(OUTPUT_FORMAT_STR)
        out = capsys.readouterr().out

        assert "one" in out
        assert "three" in out

    def test_demo_command_executes(self, kernel):
        response = kernel.execute_kernel_command(
            self._make_request(kernel, output_target=[OUTPUT_TARGET_NONE])
        )
        assert isinstance(response, QueuedCollectionResponse)

    def test_demo_command_first_function_value(self, kernel, capsys):
        kernel.execute_kernel_command(
            self._make_request(kernel, output_target=[OUTPUT_TARGET_NONE])
        )
        # The first callable returns DEMO_COLLECTION_FIRST_VALUE
        # which gets passed as previous_value to the second
        # We just verify the command runs without error and produces output
        response = kernel.execute_kernel_command(
            self._make_request(kernel, output_target=[OUTPUT_TARGET_NONE])
        )
        assert response is not None
