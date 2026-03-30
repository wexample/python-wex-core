from __future__ import annotations

import logging

from tests.abstract_kernel_test import AbstractKernelTest


class TestLogging(AbstractKernelTest):
    def test_logger_default_level(self, kernel) -> None:
        # No verbosity flags set → WARNING
        assert kernel.logger.level == logging.WARNING

    def test_logger_exists(self, kernel) -> None:
        assert kernel.logger is not None
        assert isinstance(kernel.logger, logging.Logger)

    def test_logger_goes_to_stderr(self, kernel) -> None:
        assert any(isinstance(h, logging.StreamHandler) for h in kernel.logger.handlers)

    def test_logger_name(self, kernel) -> None:
        from wexample_wex_core.const.globals import CORE_COMMAND_NAME

        assert kernel.logger.name == str(CORE_COMMAND_NAME)
