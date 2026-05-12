from __future__ import annotations

import pytest

from tests.abstract_kernel_test import AbstractKernelTest
from wexample_wex_core.const.globals import COMMAND_SEPARATOR_ADDON
from wexample_wex_core.resolver.addon_command_resolver import AddonCommandResolver


class TestCoreAutocompletesSuggest(AbstractKernelTest):
    @pytest.fixture
    def resolver(self, kernel) -> AddonCommandResolver:
        for r in kernel.get_resolvers().values():
            if isinstance(r, AddonCommandResolver):
                return r
        raise RuntimeError("AddonCommandResolver not found")

    def _suggest(self, resolver: AddonCommandResolver, search: str, cursor: int) -> str:
        search_split = search.split(" ") if search.strip() else [""]
        return resolver.autocomplete_suggest(cursor, search_split) or ""

    def test_empty_search_returns_multiple_addon_names(self, resolver) -> None:
        result = self._suggest(resolver, "", 0)
        parts = result.split()
        assert len(parts) >= 2
        # No "::" when multiple matches
        assert all("::" not in p for p in parts)

    def test_single_match_appends_separator(self, resolver) -> None:
        # "demo" is unambiguous — should return "demo::"
        result = self._suggest(resolver, "demo", 0)
        assert result == "demo" + COMMAND_SEPARATOR_ADDON

    def test_partial_colon_returns_single_colon(self, resolver) -> None:
        # bash splits "core:" as ["core", ":"] — should return ":" not "::"
        result = self._suggest(resolver, "core :", 1)
        assert result == ":"

    def test_after_separator_returns_groups(self, resolver) -> None:
        result = self._suggest(resolver, "core ::", 1)
        parts = result.split()
        assert len(parts) >= 1
        assert all("/" in p for p in parts)

    def test_after_separator_filters_by_prefix(self, resolver) -> None:
        result = self._suggest(resolver, "core :: pi", 2)
        # Multiple ping/* commands may exist — just check at least one is suggested
        assert result != "" and all("ping/" in p for p in result.split())

    def test_unqualified_command(self, resolver) -> None:
        # "ping/pong" without addon prefix — should be found across all addons
        result = self._suggest(resolver, "ping/pong", 0)
        assert "ping/pong" in result

    def test_unqualified_prefix_without_slash(self, resolver) -> None:
        # typing "pin" (no slash) should suggest "ping/hi" and "ping/pong"
        # i.e. unqualified group/command shortcuts even without "/" in the typed text
        result = self._suggest(resolver, "pin", 0)
        parts = result.split()
        assert any("ping/" in p for p in parts)
