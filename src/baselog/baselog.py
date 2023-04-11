#!/usr/bin/env python3
""" sets up default a console logger and file logging for the consumer app """
import logging
import os
import time
from typing import Literal, Optional, Tuple

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def setup_logging(
    root_name: str,
    log_dir: str = "/log",
    console_log_level: LogLevel = "DEBUG",
    file_log_level: LogLevel = "DEBUG",
    log_file_timestamp: Optional[str] = None,
    datefmt: str = "%Y-%m-%dT%H:%M:%S%z",
) -> Tuple[logging.Logger, Optional[str]]:
    """
    sets up a console logger at the given log_level and if given a non-empty
    log_dir it will be created if necessary and populated with log files;
    returns a (logger, timestring) tuple
    """
    log_format = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt=datefmt,
    )

    logger = logging.getLogger(root_name)
    logger.setLevel(console_log_level)
    logging.captureWarnings(True)

    # always log to the console in a container context
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_log_level)
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)

    log_file = None
    if log_dir:
        # make the log_dir if it doesn't exist
        if not os.path.isdir(log_dir):
            os.makedirs(log_dir)

        if not log_file_timestamp:
            log_file_timestamp = time.strftime(datefmt)

        log_file = os.path.join(log_dir, f"{root_name}_{log_file_timestamp}.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(file_log_level)
        file_handler.setFormatter(log_format)
        logger.addHandler(file_handler)

    return logger, log_file
