#!/usr/bin/env python

# Basename: logging_boilerplate
# Description: Common logic for Python logging
# Version: 2.0.1
# VersionDate: 19 Oct 2021

# --- Global Logging Commands ---
# validation:           is_logger, is_handler
# logger:               get_logger
# handler:              get_handler, add_handler, set_handlers

# :: Usage Instructions ::
# * Call get_logger() to receive a root logger without handlers
# * Pass an instance of LogOptions into get_logger() to customize the logger name
#   and handlers by using LogHandlerOptions
# * The logger types are stream (console/terminal) and file-based
# * Providing 'path' to LogHandlerOptions toggles handler from stream to file

import logging, datetime, pytz, sys
import colorlog
from typing import List, Optional, Any

# ------------------------ Classes ------------------------

_timezone: str = "US/Central"
_time_format: str = "%Y-%m-%d %H:%M:%S"
_message_format: str = "%(message)s"

# Pass 'path' for file handler; must expand absolute paths ('~' treated relatively)
class LogHandlerOptions(object):
    def __init__(self, level=logging.WARNING, path="", message_format=_message_format, time_format=_time_format, timezone=_timezone):
        # levels: 10-DEBUG, 20-INFO, 30-WARNING, 40-ERROR, 50-CRITICAL
        level_choices = [10, 20, 30, 40, 50]
        if isinstance(level, int) and level in level_choices:
            self.level = level
        else:
            self.level = logging.WARNING
        self.path = str(path)
        self.message_format = str(message_format)
        self.time_format = str(time_format)
        self.timezone = str(timezone)


# Default args for logging; argparse expected to override
class LogArgs(object):
    def __init__(self, debug=False):
        self.debug = bool(debug)


# ------------------------ Global Functions ------------------------

# --- Validation Commands ---

def is_logger(log) -> bool:
    return isinstance(log, logging.Logger)


def is_handler(log) -> bool:
    return isinstance(log, logging.Handler)


# --- Logger Commands ---

_stream_handler: LogHandlerOptions = LogHandlerOptions()

def get_logger(log_name: Optional[str]="root", handlers: Optional[List[LogHandlerOptions]]=None) -> logging.Logger:
    # Automatically attach default handlers (stream handler)
    if handlers == None: handlers = [_stream_handler]
    # Obtain instance of logging.Logger based on name (idempotent)
    # logger: logging.Logger = logging.getLogger(log_name)
    logger: logging.Logger = colorlog.getLogger(log_name)
    # Set logger to lowest level because handlers will control the true level
    logger.setLevel(logging.DEBUG)
    set_handlers(logger, handlers)
    return logger


def get_handler(options: Optional[LogHandlerOptions]=None):
    if not isinstance(options, LogHandlerOptions): raise TypeError("get_handler() expects parameter 'options' as instance of LogHandlerOptions")
    if options.path:
        # Setup a file handler for writing to log file
        handler = logging.FileHandler(filename=options.path)
    else:
        # Setup a stream handler for live console output (stdout/stderr); stderr is default
        # handler = logging.StreamHandler()
        # handler = logging.StreamHandler(sys.stdout)
        handler = colorlog.StreamHandler(sys.stdout)
    # Create formatter to attach to handler
    # log_formatter = logging.Formatter(fmt=options.message_format, datefmt=options.time_format)
    log_formatter = colorlog.ColoredFormatter(options.message_format, datefmt=options.time_format)
    log_formatter.converter = _get_timezone_converter(options.timezone)
    # Configure handler with log format and level
    handler.setFormatter(log_formatter)
    handler.setLevel(options.level)
    return handler


# Generate handler from LogHandlerOptions and attach to logger
def add_handler(logger: logging.Logger, options: Optional[LogHandlerOptions]=None):
    if not is_logger(logger): raise TypeError("add_handler() expects parameter 'logger' as instance of logging.Logger")
    if not isinstance(options, LogHandlerOptions): raise TypeError("add_handler() expects parameter 'options' as instance of LogHandlerOptions")
    handler = get_handler(options)
    logger.addHandler(handler)


# Apply batch of handlers to logger based on list of LogHandlerOptions
def set_handlers(logger: logging.Logger, handlers: Optional[List[LogHandlerOptions]]=None):
    if isinstance(handlers, type(None)): handlers = []
    if not is_logger(logger): raise TypeError("parameter 'logger' expected as instance of logging.Logger")
    if not _valid_handlers(handlers): raise TypeError("parameter 'handlers' expected as list of LogHandlerOptions instances")
    # Clear all pre-existing handlers attached to logger
    for handler in logger.handlers:
        logger.removeHandler(handler)
    # Generate batch of handlers and attach each to logger
    for options in handlers:
        add_handler(logger, options)


# Generate handlers with a standard configuration
def gen_basic_handlers(debug: Optional[bool]=False, log_path: Optional[str]="") -> List[LogHandlerOptions]:
    # https://docs.python.org/3/library/logging.html#logrecord-attributes
    # _message_format = "%(asctime)s %(name)s\t[%(levelname)s]\t%(message)s"
    # _message_format = "%(asctime)s %(levelname)-7s %(message)s"
    # _message_format = "%(asctime)s [%(levelname)s] %(message)s"
    if debug:
        log_level = 10 # logging.DEBUG
        # log_format = "%(asctime)s [%(levelname).1s] (%(module)s:%(funcName)s): %(message)s"
        log_format = "%(log_color)s%(asctime)s [%(levelname).1s] (%(module)s:%(funcName)s): %(message)s"
    else:
        log_level = 20 # logging.INFO
        log_format = "%(message)s"
    # Create stream handler (console/terminal)
    log_stream_options = LogHandlerOptions(log_level, "", log_format)
    log_handlers = [log_stream_options]
    # Create file handler when path is provided
    if log_path:
        log_file_options = LogHandlerOptions(log_level, log_path, log_format)
        log_handlers.append(log_file_options)
    return log_handlers


# --- Private Commands ---

# Convert to timezone for log output
def _get_timezone_converter(timezone="UTC"):
    def format_timezone(*args):
        utc_date = pytz.utc.localize(datetime.datetime.utcnow())
        tz = pytz.timezone(timezone)
        converted = utc_date.astimezone(tz)
        return converted.timetuple()
    return format_timezone


# Validate a list of LogHandlerOptions instances was passed
def _valid_handlers(handlers=None):
    if isinstance(handlers, type(None)): handlers = []
    invalid = False
    if isinstance(handlers, list):
        for handler in handlers:
            if not isinstance(handler, LogHandlerOptions): invalid = True
    else:
        invalid = True
    return (not invalid)


# ------------------------ Main Program ------------------------

# # Replace built-in level names
# logging.addLevelName(logging.WARNING, "WARN")
# logging.addLevelName(logging.CRITICAL, "FATAL")

# Initialize the logger
basename: str = "logging_boilerplate"
args: LogArgs = LogArgs() # for external modules
_log: logging.Logger = get_logger(basename)

if __name__ == "__main__":
    # Configure the logger
    log_level: int = 10 # logging.DEBUG
    # Pass 'path' for file handler; must expand absolute paths ('~' treated relatively)
    log_file: str = "/home/david/logs/{0}.log".format(basename)
    # Set the log handler options
    log_stream_options: LogHandlerOptions = LogHandlerOptions(log_level)
    log_file_options: LogHandlerOptions = LogHandlerOptions(log_level, log_file)
    # Refresh logger with the new handlers
    log_handlers: List[LogHandlerOptions] = [log_stream_options, log_file_options]
    set_handlers(_log, log_handlers)

    _log.debug("--- Log test successful! ---")
    _log.info("--- Log test successful! ---")
    _log.warning("--- Log test successful! ---")
    _log.error("--- Log test successful! ---")
    _log.critical("--- Log test successful! ---")

    _log.warning("log handler count: {0}".format(len(_log.handlers)))
    _log.warning("log handlers: {0}".format(_log.handlers))

    # --- Usage Example ---
    # python $HOME/.local/lib/python3.6/site-packages/logging_boilerplate.py
