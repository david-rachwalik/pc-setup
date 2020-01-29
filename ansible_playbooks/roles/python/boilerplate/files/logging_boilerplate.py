#!/usr/bin/env python

# Basename: logging_boilerplate
# Description: Common logic to generate log handlers as needed
# Version: 1.1
# VersionDate: 08 Jan 2020

import logging, datetime, pytz

# ------------------------ Classes ------------------------

def IsLogger(logger):
    return isinstance(logger, logging.Logger)


class LoggerOptions(object):
    def __init__(self, name="", level=logging.WARN, filePath="", logFormat=""):
        self.name = str(name)
        # Minimum level of message to log: DEBUG(10)|INFO(20)|WARN(30)|ERROR(40)|FATAL(50)
        self.level = int(level)
        self.path = str(filePath)
        self.format = str(logFormat)


# Convert the timezone for log output
def DisplayTime(*args):
    utc_date = pytz.utc.localize(datetime.datetime.utcnow())
    timezone = pytz.timezone("US/Central")
    converted = utc_date.astimezone(timezone)
    return converted.timetuple()


# Accepts a pre-instantiated logger or LoggerOptions
class LogManager(object):
    def __init__(self, item=None):
        self.logger = None
        # Initialize the logger
        if IsLogger(item):
            self.logger = item
        elif isinstance(item, LoggerOptions):
            # Obtain instance of logging.Logger based on name (idempotent)
            self.logger = logging.getLogger(item.name)
            # Initialize logger output settings and handlers
            if not self.logger.handlers:
                self.logger.setLevel(item.level)
                self.AddHandler(item.level, item,.path)
                self.logger.debug("(LogManager:__init__) '{0}' logger initialized".format(item.name))
        else:
            # Obtain root instance of logging.Logger
            self.logger = logging.getLogger()


    # ciectld-1.1 used logging.basicConfig to create a root logger with default StreamHandler
    # LogManager generates handlers as needed
    def AddHandler(self, level=logging.WARN, filePath="")::
        # Create formatter to attach to handler
        # logMessageFormat = "/%(asctime)s/ [%(levelname)s] %(message)s"
        # logMessageFormat = "[%(levelname)s] %(asctime)s # %(message)s"
        logMessageFormat = "%(asctime)s [%(levelname)s] %(message)s"
        # logTimeFormat = "%Y%b%d %H:%M:%S"
        logTimeFormat = "%Y-%m-%d %H:%M:%S"
        logging.Formatter.converter = DisplayTime

        # TODO: FileHandler minimally tested; improve filePath validation
        if filePath != "":
            # Setup a file handler for writing to a log file
            handler = logging.FileHandler(filename=filePath)
        else:
            # Setup a stream handler for live console output (stdout/stderr)
            handler = logging.StreamHandler()
        # Configure handler with log level and formatter
        handler.setLevel(level)
        handler.setFormatter(logFormatter)
        self.logger.addHandler(handler)


# ------------------------ Main Program ------------------------

if __name__ == '__main__':
    boilerplate = LogManager()
    boilerplate.Exit()
