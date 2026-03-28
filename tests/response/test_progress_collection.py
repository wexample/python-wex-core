from wexample_app.const.output import OUTPUT_FORMAT_JSON, OUTPUT_FORMAT_STR, OUTPUT_TARGET_NONE
from wexample_app.response.dict_response import DictResponse
from wexample_wex_core.response.progress_collection_response import ProgressCollectionResponse
from wexample_wex_core.response.queue_collection.queued_collection_stop_response import QueuedCollectionStopResponse

from tests.response.abstract_response_test import AbstractResponseTest


class TestProgressCollectionResponse(AbstractResponseTest):
    def create_response(self, kernel) -> ProgressCollectionResponse:
        return ProgressCollectionResponse(
            kernel=kernel,
            title="Test progress",
            content=[
                DictResponse(kernel=kernel, content={"step": "one"}),
                DictResponse(kernel=kernel, content={"step": "two"}),
            ],
        )

    def get_command(self):
        from wexample_wex_core.addons.demo.commands.response.progress import demo__response__progress
        return demo__response__progress

    def get_command_arguments(self) -> dict:
        return {}

    def test_renders_all_steps(self, kernel, capsys):
        self.create_response(kernel).get_formatted(OUTPUT_FORMAT_STR)
        out = capsys.readouterr().out

        assert "one" in out
        assert "two" in out

    def test_title_in_printable(self, kernel):
        # Title is in the progress bar (terminal io), not in capsys stdout
        # Verify it's accessible via get_printable
        response = self.create_response(kernel)
        assert "Test progress" in response.get_printable()

    def test_step_labels_stored(self, kernel):
        response = ProgressCollectionResponse(
            kernel=kernel,
            title="Labeled",
            step_labels=["First step", "Second step"],
            content=[
                DictResponse(kernel=kernel, content={"a": "1"}),
                DictResponse(kernel=kernel, content={"b": "2"}),
            ],
        )
        assert response.step_labels == ["First step", "Second step"]

    def test_previous_value_chained(self, kernel):
        received = []

        def step_b(previous_value):
            received.append(previous_value)
            return "done"

        ProgressCollectionResponse(
            kernel=kernel,
            title="Chain test",
            content=[
                DictResponse(kernel=kernel, content={"val": "x"}),
                step_b,
            ],
        ).get_formatted(OUTPUT_FORMAT_STR)

        assert received == [{"val": "x"}]

    def test_stop_halts(self, kernel, capsys):
        ProgressCollectionResponse(
            kernel=kernel,
            title="Stop test",
            content=[
                DictResponse(kernel=kernel, content={"step": "one"}),
                QueuedCollectionStopResponse(kernel=kernel, reason="halt"),
                DictResponse(kernel=kernel, content={"step": "three"}),
            ],
        ).get_formatted(OUTPUT_FORMAT_STR)
        out = capsys.readouterr().out

        assert "one" in out
        assert "three" not in out

    def test_nested_progress(self, kernel, capsys):
        sub = ProgressCollectionResponse(
            kernel=kernel,
            title="Sub task",
            content=[
                DictResponse(kernel=kernel, content={"sub": "step"}),
            ],
        )
        ProgressCollectionResponse(
            kernel=kernel,
            title="Main task",
            content=[
                DictResponse(kernel=kernel, content={"main": "step"}),
                sub,
            ],
        ).get_formatted(OUTPUT_FORMAT_STR)
        out = capsys.readouterr().out

        # Steps content is captured, progress bar titles go through terminal io
        assert "main" in out
        assert "sub" in out

    def test_empty_collection(self, kernel):
        ProgressCollectionResponse(
            kernel=kernel,
            title="Empty",
            content=[],
        ).get_formatted(OUTPUT_FORMAT_STR)

    def test_progress_inside_queued(self, kernel, capsys):
        from wexample_wex_core.response.queued_collection_response import QueuedCollectionResponse

        QueuedCollectionResponse(
            kernel=kernel,
            content=[
                DictResponse(kernel=kernel, content={"step": "one"}),
                ProgressCollectionResponse(
                    kernel=kernel,
                    title="Sub progress",
                    content=[
                        DictResponse(kernel=kernel, content={"sub": "step"}),
                    ],
                ),
            ],
        ).get_formatted(OUTPUT_FORMAT_STR)
        out = capsys.readouterr().out

        assert "one" in out
        assert "sub" in out

    def test_queued_inside_progress(self, kernel, capsys):
        from wexample_wex_core.response.queued_collection_response import QueuedCollectionResponse

        ProgressCollectionResponse(
            kernel=kernel,
            title="Main progress",
            content=[
                DictResponse(kernel=kernel, content={"step": "one"}),
                QueuedCollectionResponse(
                    kernel=kernel,
                    content=[
                        DictResponse(kernel=kernel, content={"queued": "step"}),
                    ],
                ),
            ],
        ).get_formatted(OUTPUT_FORMAT_STR)
        out = capsys.readouterr().out

        assert "one" in out
        assert "queued" in out

    def test_demo_command_executes(self, kernel):
        response = kernel.execute_kernel_command(
            self._make_request(kernel, output_target=[OUTPUT_TARGET_NONE])
        )
        assert isinstance(response, ProgressCollectionResponse)
