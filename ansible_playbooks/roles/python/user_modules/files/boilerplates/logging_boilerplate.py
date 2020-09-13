#!/usr/bin/env python

# Basename: logging_boilerplate
# Description: Common logic for Python logging
# Version: 1.3.2
# VersionDate: 27 Aug 2020

import logging, datetime, pytz

try:
    # Python 2 has both 'str' (bytes) and 'unicode' text
    basestring = basestring
    unicode = unicode
except NameError:
    # Python 3 names the unicode data type 'str'
    basestring = str
    unicode = str

# ------------------------ Classes ------------------------

def is_logger(log):
    return isinstance(log, logging.Logger)


# defaultMessageFormat = "%(asctime)s %(name)s\t[%(levelname)s]\t%(message)s"
# defaultMessageFormat = "%(asctime)s %(levelname)-7s %(message)s"
# defaultMessageFormat = "%(asctime)s [%(levelname)s] %(message)s"

# Restrict output to 1 character
# defaultMessageFormat = "%(asctime)s [%(levelname).1s] %(message)s"
defaultMessageFormat = "%(asctime)s [%(levelname).1s] %(name)s:%(message)s"


# Levels: 10-DEBUG, 20-INFO, 30-WARNING, 40-ERROR, 50-CRITICAL
class LogOptions(object):
    def __init__(self, name="", level=logging.WARNING, path="", messageFormat=defaultMessageFormat, timeFormat="%Y-%m-%d %H:%M:%S", timezone="US/Central"):
        self.name = str(name)
        self.level = int(level)
        self.path = str(path)
        self.messageFormat = str(messageFormat)
        self.timeFormat = str(timeFormat)
        self.timezone = str(timezone)


# Accepts logging.Logger, LogOptions, or string; defaults to root logger without handlers
# Providing LogOptions will establish the first handler automatically
def get_logger(log):
    logger = None
    # Initialize the logger
    if is_logger(log):
        return log
    elif isinstance(log, LogOptions):
        logger = get_logger(log.name)
        logger.setLevel(log.level)
        # Initialize a logger output handler
        if not logger.handlers:
            logger = add_log_handler(logger, log.level, log.path, log.messageFormat, log.timeFormat, log.timezone)
    elif log and isinstance(log, str):
        # Obtain instance of logging.Logger based on name (idempotent)
        logger = logging.getLogger(log)
    else:
        # Obtain root instance of logging.Logger
        # logger = logging.getLogger()
        logger = logging.getLogger(__name__)
    return logger


def add_log_handler(logger, level=logging.WARNING, path="", messageFormat="", timeFormat="", timezone=""):
    if not is_logger(logger): return
    # Replace built-in level names
    logging.addLevelName(logging.WARNING, "WARN")
    logging.addLevelName(logging.CRITICAL, "FATAL")
    # Create formatter to attach to handler
    logFormatter = logging.Formatter(fmt=messageFormat, datefmt=timeFormat)
    logFormatter.converter = get_timezone_converter(timezone)
    if path:
        # Setup a file handler for writing to a log file
        handler = logging.FileHandler(filename=path)
    else:
        # Setup a stream handler for live console output (stdout/stderr)
        handler = logging.StreamHandler()
    # Configure handler with formatter (only set log level to logger, ignoring handlers)
    # handler.setLevel(level)
    handler.setFormatter(logFormatter)
    logger.addHandler(handler)
    return logger


# Convert to timezone for log output
def get_timezone_converter(timezone="UTC"):
    def format_timezone(*args):
        utc_date = pytz.utc.localize(datetime.datetime.utcnow())
        tz = pytz.timezone(timezone)
        converted = utc_date.astimezone(tz)
        return converted.timetuple()
    return format_timezone


# ------------------------ Main Program ------------------------

# Initialize the logger
basename = "logging_boilerplate"
log_options = LogOptions(basename)
logger = get_logger(log_options)

if __name__ == "__main__":
    # Configure the logger
    logger = get_logger(basename)
    log_level = 10 # logging.DEBUG
    logger.setLevel(log_level)
    logger.info("Log test successful!")

    # python $HOME/.local/lib/python2.7/site-packages/logging_boilerplate.py
    # python $HOME/.local/lib/python3.6/site-packages/logging_boilerplate.py
