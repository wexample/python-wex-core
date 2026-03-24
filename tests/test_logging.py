import logging


def test_logger_exists(kernel):
    assert kernel.logger is not None
    assert isinstance(kernel.logger, logging.Logger)


def test_logger_name(kernel):
    from wexample_wex_core.const.globals import CORE_COMMAND_NAME

    assert kernel.logger.name == str(CORE_COMMAND_NAME)


def test_logger_default_level(kernel):
    # No verbosity flags set → WARNING
    assert kernel.logger.level == logging.WARNING


def test_logger_goes_to_stderr(kernel):
    assert any(
        isinstance(h, logging.StreamHandler) for h in kernel.logger.handlers
    )
