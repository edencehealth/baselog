#!/usr/bin/env python3
""" implements the BaseLog class, a helper for standardizing logging across projects """
# pylint: disable=too-many-instance-attributes
import itertools
import logging
import math
import os
import sys
import time
import traceback
from types import TracebackType
from typing import Any, Final, Literal, Optional, Tuple, Type, Union

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

# these next 2 annotations inspired by: https://stackoverflow.com/a/75384545
_SysExcInfoType = Union[
    Tuple[type[BaseException], BaseException, Optional[TracebackType]],
    Tuple[None, None, None],
]
_ExcInfoType = Union[None, bool, _SysExcInfoType, BaseException]

DEFAULT_LOGFMT: Final[str] = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_DATEFMT: Final[str] = "%Y-%m-%dT%H:%M:%S%z"


class BaseLog:
    """standard class for logging in a 12-factor application"""

    root_name: str
    root_logger: logging.Logger
    log_dir: Optional[str]
    log_file_name: Optional[str]
    log_file: Optional[str]
    console_log_level: LogLevel
    console_logfmt: str
    console_datefmt: str
    file_log_level: LogLevel
    file_logfmt: str
    file_datefmt: str

    def __init__(
        self,
        root_name: str,
        log_dir: Optional[str] = "/log",
        log_file_name: Optional[str] = None,
        console_log_level: LogLevel = "DEBUG",
        console_logfmt: Optional[str] = None,
        console_datefmt: Optional[str] = None,
        file_log_level: LogLevel = "DEBUG",
        file_logfmt: Optional[str] = None,
        file_datefmt: Optional[str] = None,
    ) -> None:
        self.root_name = root_name
        self.log_dir = log_dir
        self.log_file_name = log_file_name
        self.console_log_level = console_log_level
        self.console_logfmt = console_logfmt or DEFAULT_LOGFMT
        self.console_datefmt = console_datefmt or DEFAULT_DATEFMT
        self.file_log_level = file_log_level
        self.file_logfmt = file_logfmt or DEFAULT_LOGFMT
        self.file_datefmt = file_datefmt or DEFAULT_DATEFMT
        self.setup_loggers()

    def setup_loggers(self) -> None:
        """
        sets up a console logger (and optionally a file logger) at the specified
        log_levels;
        """
        self.root_logger = logging.getLogger(self.root_name)
        self.root_logger.setLevel(logging.DEBUG)
        logging.captureWarnings(True)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.console_log_level)
        console_handler.setFormatter(
            logging.Formatter(
                fmt=self.console_logfmt,
                datefmt=self.console_datefmt,
            )
        )
        self.root_logger.addHandler(console_handler)
        sys.excepthook = self.handle_uncaught_exception

        if self.log_dir:
            if not os.path.isdir(self.log_dir):
                # if given a log_dir that doesn't exist we try to create it
                os.makedirs(self.log_dir)

            if not self.log_file_name:
                self.log_file_name = (
                    f"{self.root_name}_{time.strftime(self.file_datefmt)}.log"
                )
            self.log_file = os.path.join(self.log_dir, self.log_file_name)
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setLevel(self.file_log_level)
            file_handler.setFormatter(
                logging.Formatter(
                    fmt=self.file_logfmt,
                    datefmt=self.file_datefmt,
                )
            )
            self.root_logger.addHandler(file_handler)

    def handle_uncaught_exception(
        self,
        exception_type: Type[BaseException],
        exception: BaseException,
        _traceback: Optional[TracebackType],
    ):
        """
        handle_uncaught_exception is intended to be called as a sys.excepthook
        which gets called when an exception is otherwise uncaught
        see: https://docs.python.org/3/library/sys.html#sys.excepthook
        """
        self.root_logger.critical("uncaught %s exception:", exception_type.__name__)

        exception_lines = str(exception).splitlines()
        log_msg = f"exception L{self.zeropad_fmt(len(exception_lines))}: %s"
        for i, line in enumerate(exception_lines):
            self.root_logger.critical(log_msg, i, line.rstrip())

        if _traceback is not None:
            frames = traceback.format_exception(exception_type, exception, _traceback)
            tb_lines = list(itertools.chain(*[frame.splitlines() for frame in frames]))
            log_msg = f"traceback L{self.zeropad_fmt(len(tb_lines))}: %s"
            for i, line in enumerate(tb_lines):
                self.root_logger.critical(log_msg, i, line.rstrip())

    def __getattr__(self, name: str) -> Any:
        """forwards unknown attribute access to our root_logger instance variable"""
        # https://docs.python.org/3/reference/datamodel.html?highlight=__getattr__#object.__getattr__
        return getattr(self.root_logger, name)

    @staticmethod
    def zeropad_fmt(maxval: int) -> str:
        """print the log message template for zero-padding numbers up to max_value in size"""
        length: int
        if maxval == 0:
            length = 1
        else:
            # leave room for the sign?
            length = 1 if maxval > 0 else 2
            length += int(math.log10(abs(maxval)))

        return f"%0{length}d"
