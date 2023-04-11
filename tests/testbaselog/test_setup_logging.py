#!/usr/bin/env python3
""" test configuration via command-line arguments """
import os
import re
from typing import Final

from baselog import setup_logging

# REGEX_TS is a regex segment (string) which matches timestamps used in this library
#   e.g. timestamps like: 2023-04-11T11:16:43+0200
REGEX_TS: Final[str] = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{4}"


# this should probably be a fixture
def read_file_text(path: str, encoding="utf-8", errors=None) -> str:
    """reads the contents of the given file and returns them as a string"""
    with open(path, "rt", encoding=encoding, errors=errors) as textfile:
        return textfile.read()


def test_basics(tmp_log_dir, capsys):
    """test basic operation of baselog"""
    logger, log_file = setup_logging(
        "testapp",
        log_dir=tmp_log_dir,
        console_log_level="DEBUG",
        file_log_level="DEBUG",
    )
    assert os.path.exists(log_file)

    logger.debug("I'm a log message at debug level!")
    logger.info("I'm a log message at info level!")
    logger.warning("I'm a log message at warning level!")
    logger.error("I'm a log message at error level!")
    logger.critical("I'm a log message at critical level!")
    captured = capsys.readouterr()

    expected_contents = ""
    for level in ("debug", "info", "warning", "error", "critical"):
        expected_contents += (
            f"{REGEX_TS} - testapp - {level.upper()} - "
            f"I'm a log message at {level} level!\n"
        )

    assert re.match(f"^{expected_contents}$", captured.err)
    assert re.match(f"^{expected_contents}$", read_file_text(log_file))
