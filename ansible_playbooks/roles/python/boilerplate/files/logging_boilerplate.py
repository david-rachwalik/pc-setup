#!/usr/bin/env python

# Basename: logging_boilerplate
# Description: Common logic for logging
# Version: 1.3
# VersionDate: 29 Jan 2020

import logging, datetime, pytz

# ------------------------ Classes ------------------------

# Levels: 10-DEBUG, 20-INFO, 30-WARN, 40-ERROR, 50-FATAL
class LogOptions(object):
    def __init__(self, name="", level=logging.WARN, path="", messageFormat="%(asctime)s [%(levelname)s] %(message)s", timeFormat = "%Y-%m-%d %H:%M:%S"):
        self.name = str(name)
        self.level = int(level)
        self.path = str(path)
        self.messageFormat = str(messageFormat)
        self.timeFormat = str(timeFormat)


# Accepts logging.Logger, LogOptions, or string; defaults to root logger without handlers
# Providing LogOptions will establish the first handler automatically
def Logger(log, level=logging.WARN, path="", messageFormat="", timeFormat=""):
    logger = None
    # Instialize the logger
    if isinstance(log, logging.Logger):
        return log
    elif isinstance(log, LogOptions):
        logger = Logger(log.name)
        logger.setLevel(log.level)
        # Initialize a logger output handler
        if not logger.handlers:
            logger = AddLogHandler(logger, log.level, log.path, log.messageFormat, log.timeFormat)
            logger.debug("(Logger:__init__): '{0}' logger initialized".format(log.name))
    elif isinstance(log, str) or isinstance(log, unicode):
        # Obtain instance of logging.Logger based on name (idempotent)
        logger = logging.getLogger(log)
    else:
        # Obtain root instance of logging.Logger
        logger = logging.getLogger()
    return logger


def AddLogHandler(logger, level=logging.WARN, path="", messageFormat="", timeFormat="", timeConverter=None):
    if not isinstance(logger, logging.Logger): return
    # Create formatter to attach to handler
    logFormatter = logging.Formatter(fmt=messageFormat, datefmt=timeFormat)
    logFormatter.converter = timeConverter if callable(timeConverter) else DisplayTime
    if path:
        # Setup a file handler for writing to a log file
        handler = logging.FileHandler(filename=path)
    else:
        # Setup a stream handler for live console output (stdout/stderr)
        handler = logging.StreamHandler()
    # Configure handler with log level and formatter
    handler.setLevel(level)
    handler.setFormatter(logFormatter)
    logger.addHandler(handler)
    return logger


# Convert to timezone for log output
def DisplayTime(*args):
    utc_date = pytz.utc.localize(datetime.datetime.utcnow())
    timezone = pytz.timezone("US/Central")
    converted = utc_date.astimezone(timezone)
    return converted.timetuple()


# ------------------------ Main Program ------------------------

if __name__ == "__main__":
    testLogOptions = LogOptions("test", 10)
    log = Logger(testLogOptions)
    log.info("Logger test successful!")
