#!/usr/bin/env python

# Basename: logging_boilerplate
# Description: Common logic to generate log handlers as needed
# Version: 0.5
# VersionDate: 13 Dec 2019

import logging, datetime, pytz

# ------------------------ Classes ------------------------

class LogManager(object):
    def __init__(self, logLevel=logging.INFO, logFile=""):
        # Minimum level of message to log: DEBUG(10)|INFO(20)|WARN|ERROR|FATAL
        self.logLevel = logLevel
        # Create formatter to attach to handlers
        # logMessageFormat = "/%(asctime)s/ [%(levelname)s] %(message)s"
        # logMessageFormat = "[%(levelname)s] %(asctime)s # %(message)s"
        logMessageFormat = "%(asctime)s [%(levelname)s] %(message)s"
        # logTimeFormat = "%Y%b%d %H:%M:%S"
        logTimeFormat = "%Y-%m-%d %H:%M:%S"
        self.logFormatter = logging.Formatter(fmt=logMessageFormat, datefmt=logTimeFormat)
        logging.Formatter.converter = self.DisplayTime()
        # Create logger with file basename (no extension)
        self.log = logging.getLogger(__name__)
        self.log.setLevel(self.logLevel)
        self.AddHandler(logFile)


    # ciectld-1.1 used logging.basicConfig to create a root logger with default StreamHandler
    # LogManager generates handlers as needed
    def AddHandler(self, _logFile=""):
        if isinstance(logFile, str) and len(logFile) > 0:
            # Setup a file handler for writing to a log file
            handler = logging.FileHandler(filename=logFile)
        else:
            # Setup a stream handler for live console output (stdout/stderr)
            handler = logging.StreamHandler()
        # Configure handler with log level and formatter
        handler.setLevel(self.logLevel)
        handler.setFormatter(self.logFormatter)
        self.log.addHandler(handler)


    # Convert the timezone for log output
    def DisplayTime(self, *args):
        utc_date = pytz.utc.localize(datetime.datetime.utcnow())
        timezone = pytz.timezone("US/Central")
        converted = utc_date.astimezone(timezone)
        return converted.timetuple()


# ------------------------ Main Program ------------------------

if __name__ == '__main__':
    boilerplate = ShellManager()
    boilerplate.Exit()
