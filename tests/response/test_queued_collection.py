from wexample_app.const.output import OUTPUT_FORMAT_JSON, OUTPUT_FORMAT_STR, OUTPUT_TARGET_NONE
from wexample_wex_core.response.dict_response import DictResponse
from wexample_wex_core.response.list_response import ListResponse
from wexample_wex_core.response.queued_collection_response import QueuedCollectionResponse
from wexample_wex_core.response.queue_collection.queued_collection_stop_response import QueuedCollectionStopResponse
from wexample_wex_core.response.queue_collection.queued_collection_stop_current_step_response import QueuedCollectionStopCurrentStepResponse

from tests.response.abstract_response_test import AbstractResponseTest


class TestQueuedCollectionResponse(AbstractResponseTest):
    def create_response(self, kernel) -> QueuedCollectionResponse:
        return QueuedCollectionResponse(
            kernel=kernel,
            content=[
                DictResponse(kernel=kernel, content={"step": "one"}),
                DictResponse(kernel=kernel, content={"step": "two"}),
            ],
        )

    def get_command(self):
        from wexample_wex_core.addons.demo.commands.ping.pong import demo__ping__pong

        return demo__ping__pong

    def get_command_arguments(self) -> dict:
        return {"type": "queued"}

    def test_str_renders_all_steps(self, kernel, capsys):
        self.create_response(kernel).get_formatted(OUTPUT_FORMAT_STR)
        out = capsys.readouterr().out

        assert "one" in out
        assert "two" in out

    def test_stop_halts_queue(self, kernel, capsys):
        response = QueuedCollectionResponse(
            kernel=kernel,
            content=[
                DictResponse(kernel=kernel, content={"step": "one"}),
                QueuedCollectionStopResponse(kernel=kernel, reason="test-stop"),
                DictResponse(kernel=kernel, content={"step": "three"}),
            ],
        )
        response.get_formatted(OUTPUT_FORMAT_STR)
        out = capsys.readouterr().out

        assert "one" in out
        assert "three" not in out

    def test_stop_current_step_skips_and_continues(self, kernel, capsys):
        response = QueuedCollectionResponse(
            kernel=kernel,
            content=[
                DictResponse(kernel=kernel, content={"step": "one"}),
                QueuedCollectionStopCurrentStepResponse(kernel=kernel, reason="skip"),
                DictResponse(kernel=kernel, content={"step": "three"}),
            ],
        )
        response.get_formatted(OUTPUT_FORMAT_STR)
        out = capsys.readouterr().out

        assert "one" in out
        assert "three" in out

    def test_callable_receives_previous_value(self, kernel, capsys):
        received = []

        def step_two(previous_value):
            received.append(previous_value)
            return DictResponse(kernel=kernel, content={"got": str(previous_value)})

        QueuedCollectionResponse(
            kernel=kernel,
            content=[
                DictResponse(kernel=kernel, content={"step": "one"}),
                step_two,
            ],
        ).get_formatted(OUTPUT_FORMAT_STR)

        assert len(received) == 1
        assert received[0] == {"step": "one"}

    def test_ping_returns_queued_response(self, kernel):
        response = kernel.execute_kernel_command(self._make_request(kernel, output_target=[OUTPUT_TARGET_NONE]))
        assert isinstance(response, QueuedCollectionResponse)
