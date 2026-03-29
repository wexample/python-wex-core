from tests.abstract_kernel_test import AbstractKernelTest


class TestAutocompleteSuggest(AbstractKernelTest):
    def _suggest(self, kernel, search: str, cursor: int = 0) -> list[str]:
        from wexample_app.const.output import OUTPUT_TARGET_NONE
        from wexample_app.response.str_response import StrResponse
        from wexample_wex_core.common.command_request import CommandRequest

        request = CommandRequest(
            kernel=kernel,
            name="default::autocomplete/suggest",
            output_target=[OUTPUT_TARGET_NONE],
            arguments={"search": search, "cursor": cursor},
        )
        response = kernel.execute_kernel_command(request)
        assert isinstance(response, StrResponse)
        return response.content.split() if response.content.strip() else []

    def test_suggests_by_prefix(self, kernel):
        results = self._suggest(kernel, "demo::")
        assert "demo::ping/pong" in results
        assert "demo::sudo/check" in results

    def test_filters_by_prefix(self, kernel):
        results = self._suggest(kernel, "demo::p")
        assert "demo::ping/pong" in results
        assert "demo::sudo/check" not in results

    def test_suggests_alias(self, kernel):
        results = self._suggest(kernel, "pi")
        assert "ping" in results

    def test_empty_search_returns_all(self, kernel):
        results = self._suggest(kernel, "")
        assert len(results) > 0

    def test_no_match_returns_empty(self, kernel):
        results = self._suggest(kernel, "zzznomatch")
        assert results == []

    def test_cursor_out_of_bounds_returns_empty(self, kernel):
        results = self._suggest(kernel, "demo::ping/pong", cursor=5)
        assert results == []
