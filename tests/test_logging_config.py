r"""Feature: Logging of every run to the console and to a file

  As a Content Enricher user
  I want the whole process written to a log file
  So that I can review what happened after the run
"""

import logging

from src.logging_config import DEFAULT_LOG_FILE, setup_logging


def _handlers_to(logger: logging.Logger, log_file) -> list:
    target = str(log_file.resolve())
    return [
        handler
        for handler in logger.handlers
        if isinstance(handler, logging.FileHandler)
        and handler.baseFilename == target
    ]


def test_setup_logging_creates_the_log_file(tmp_path):
    r"""@successful

    Scenario: Write the messages of a run into the log file
        Given a log file that does not exist yet
        When the logging is set up
        And a message is logged
        Then the log file exists
        And the file contains the message
        And the file contains the level "[INFO]"
        And a FileHandler is attached to that file
    """
    log_file = tmp_path / "logs" / "app.log"
    logger = setup_logging(log_file=str(log_file))

    logger.info("Mensaje de prueba 12345")

    assert log_file.exists()
    content = log_file.read_text(encoding="utf-8")
    assert "Mensaje de prueba 12345" in content
    assert "[INFO]" in content
    assert _handlers_to(logger, log_file), "A FileHandler must be configured for the log file"


def test_setup_logging_is_idempotent(tmp_path):
    r"""@successful

    Scenario: Attach the file handler only once
        Given a log file
        When the logging is set up twice
        Then exactly one FileHandler points at that file
    """
    log_file = tmp_path / "app.log"

    setup_logging(log_file=str(log_file))
    logger = setup_logging(log_file=str(log_file))

    assert len(_handlers_to(logger, log_file)) == 1


def test_the_default_log_file_path():
    r"""@successful

    Scenario: Keep the agreed default log file path
        Given the default configuration
        When I read the default log file
        Then the path is "logs/app.log"
    """
    assert DEFAULT_LOG_FILE == "logs/app.log"
