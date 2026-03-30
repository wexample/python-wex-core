from __future__ import annotations

import json

import pytest
from wexample_app.const.output import OUTPUT_FORMAT_JSON, OUTPUT_FORMAT_STR
from wexample_app.response.boolean_response import BooleanResponse
from wexample_app.response.int_response import IntResponse
from wexample_app.response.null_response import NullResponse
from wexample_app.response.str_response import StrResponse

from tests.abstract_kernel_test import AbstractKernelTest


class TestStrResponse(AbstractKernelTest):
    def test_get_printable(self, kernel) -> None:
        assert StrResponse(kernel=kernel, content="hello").get_printable() == "hello"

    def test_rejects_non_str(self, kernel) -> None:
        with pytest.raises(Exception):
            StrResponse(kernel=kernel, content=42)

    def test_str_format(self, kernel) -> None:
        assert (
            StrResponse(kernel=kernel, content="hello").get_formatted(OUTPUT_FORMAT_STR)
            == "hello"
        )


class TestIntResponse(AbstractKernelTest):
    def test_get_printable(self, kernel) -> None:
        assert IntResponse(kernel=kernel, content=42).get_printable() == "42"

    def test_json_format(self, kernel) -> None:
        output = IntResponse(kernel=kernel, content=42).get_formatted(
            OUTPUT_FORMAT_JSON
        )
        assert json.loads(output) is not None

    def test_rejects_non_int(self, kernel) -> None:
        with pytest.raises(Exception):
            IntResponse(kernel=kernel, content="hello")


class TestBooleanResponse(AbstractKernelTest):
    def test_get_printable_true(self, kernel) -> None:
        assert BooleanResponse(kernel=kernel, content=True).get_printable() is not None

    def test_rejects_non_bool(self, kernel) -> None:
        with pytest.raises(Exception):
            BooleanResponse(kernel=kernel, content="true")


class TestNullResponse(AbstractKernelTest):
    def test_get_printable_is_none(self, kernel) -> None:
        assert NullResponse(kernel=kernel).get_printable() is None

    def test_str_format(self, kernel) -> None:
        NullResponse(kernel=kernel).get_formatted(OUTPUT_FORMAT_STR)
