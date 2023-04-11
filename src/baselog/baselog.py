#!/usr/bin/env python3
""" implements the BaseLog class, a helper for standardizing logging across projects """
# pylint: disable=too-many-instance-attributes
import itertools
import logging
import os
import sys
import time
import traceback
from types import TracebackType
from typing import Final, Literal, Mapping, Optional, Tuple, Type, Union

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
        sets up a console logger at the given log_level and if given a non-empty
        log_dir it will be created if necessary and populated with log files;
        returns a (logger, timestring) tuple
        """
        logger = logging.getLogger(self.root_name)
        logger.setLevel(self.console_log_level)
        self.root_logger = logger
        logging.captureWarnings(True)

        # always log to the console in a container context
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.console_log_level)
        console_handler.setFormatter(
            logging.Formatter(
                fmt=self.console_logfmt,
                datefmt=self.console_datefmt,
            )
        )
        logger.addHandler(console_handler)

        sys.excepthook = self.handle_uncaught_exception

        if self.log_dir:
            # make the log_dir if it doesn't exist
            if not os.path.isdir(self.log_dir):
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
            logger.addHandler(file_handler)

    def handle_uncaught_exception(
        self,
        exception_type: Type[BaseException],
        exception: BaseException,
        _traceback: Optional[TracebackType],
    ):
        """
        handler intended to be called as a sys.excepthook when an exception is uncaught
        see: https://docs.python.org/3/library/sys.html#sys.excepthook
        """
        self.root_logger.critical(
            "uncaught %s exception: %s", exception_type.__name__, exception
        )
        if _traceback is not None:
            frames = traceback.format_exception(exception_type, exception, _traceback)
            tb_lines = itertools.chain(*[frame.splitlines() for frame in frames])
            for i, line in enumerate(tb_lines):
                self.root_logger.critical("traceback-%03d: %s", i, line.rstrip())

    # the remaining functions are passthru calls to the root logger, but they
    # are richly specified (instead of just using *args, **kwargs) to make code
    # completion work better for end users

    def debug(
        self,
        msg: object,
        *args: object,
        exc_info: _ExcInfoType = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Optional[Mapping[str, object]] = None,
    ) -> None:
        """proxy to root logger's debug method"""
        self.root_logger.debug(
            msg,
            *args,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel,
            extra=extra,
        )

    def info(
        self,
        msg: object,
        *args: object,
        exc_info: _ExcInfoType = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Optional[Mapping[str, object]] = None,
    ):
        """proxy to root logger's info method"""
        self.root_logger.info(
            msg,
            *args,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel,
            extra=extra,
        )

    def warning(
        self,
        msg: object,
        *args: object,
        exc_info: _ExcInfoType = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Optional[Mapping[str, object]] = None,
    ):
        """proxy to root logger's warning method"""
        self.root_logger.warning(
            msg,
            *args,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel,
            extra=extra,
        )

    def error(
        self,
        msg: object,
        *args: object,
        exc_info: _ExcInfoType = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Optional[Mapping[str, object]] = None,
    ):
        """proxy to root logger's error method"""
        self.root_logger.error(
            msg,
            *args,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel,
            extra=extra,
        )

    def critical(
        self,
        msg: object,
        *args: object,
        exc_info: _ExcInfoType = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Optional[Mapping[str, object]] = None,
    ):
        """proxy to root logger's critical method"""
        self.root_logger.critical(
            msg,
            *args,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel,
            extra=extra,
        )
