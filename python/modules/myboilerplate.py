#!/usr/bin/python

# Basename: myboilerplate
# Version: 0.3.0
# VersionDate: 13 Aug 2019
# Description: Common business logic for *nix shell interactions

import logging
import shlex
import subprocess
import sys
import os
import shutil
from contextlib import contextmanager
import datetime
import pytz

# ------------------------ Classes ------------------------

# cietld-1.1 used logging.basicConfig to create a root logger with default StreamHandler
# LoggingBoilerplate will only generate handlers as needed


class LoggingBoilerplate(object):
    def __init__(self, logLevel=logging.INFO, logFile=""):
        # print("DEBUG (LoggingBoilerplate:__init__): Init")
        # Minimal level of message to log: DEBUG|INFO|WARN|ERROR|FATAL
        self.logLevel = logLevel
        # Create formatter to attach to handlers
        logMessageFormat = "/%(asctime)s/ [%(levelname)s] %(message)s"
        logTimeFormat = "%Y%b%d %H:%M:%S"
        self.logFormatter = logging.Formatter(fmt=logMessageFormat, datefmt=logTimeFormat)
        logging.Formatter.converter = self.DisplayTime
        # Create logger with generated name
        # self.log = logging.getLogger(__name__)
        self.log = logging.getLogger()
        self.log.setLevel(self.logLevel)
        self.AddHandler(logFile)

    def AddHandler(self, _logFile=""):
        # print("DEBUG (LoggingBoilerplate:AddHandler): Init")
        logFile = str(_logFile)
        if logFile != "":
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

    def DisplayTime(*args):
        utc_date = pytz.utc.localize(datetime.datetime.utcnow())
        timezone = pytz.timezone("US/Central")
        converted = utc_date.astimezone(timezone)
        return converted.timetuple()


class ShellBoilerplate(LoggingBoilerplate):
    def __init__(self, _baseName, logLevel=logging.INFO):
        # Initialize the inherited class constructor
        LoggingBoilerplate.__init__(self, logLevel)
        # self.log.debug("(ShellBoilerplate:__init__): Init")
        self.baseName = str(_baseName)
        self.pwd = os.getcwd()

    def Exit(self):
        # self.log.debug("(ShellBoilerplate:Exit): Init")
        sys.exit(0)

    def Fail(self):
        # self.log.debug("(ShellBoilerplate:Fail): Init")
        sys.exit(1)

    def FormatPipe(self, text):
        # Split newlines and strip/trim whitespace
        whitespaceTrimmed = str(text).strip()
        if len(whitespaceTrimmed) == 0:
            return ""
        if whitespaceTrimmed.endswith("\n"):
            return whitespaceTrimmed[-2]
        else:
            return whitespaceTrimmed

    # Creates and returns an async process to await

    def ProcessAsync(self, _command, _path=""):
        path = str(_path)
        # Ensure commands are provided as a sequence/list
        if isinstance(_command, list):
            command = _command
        elif is isinstance(_command, str):
            command = shlex.split(_command)
        else:
            return None

        if path == "":
            try:
                return subprocess.Popen(command, close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except Exception:
                return None
        else:
            with self.ChangeDirectory(path):
                try:
                    return subprocess.Popen(command, close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                except Exception:
                    return None

    # Waits for process to finish and returns output tuple (rc, stdout, stderr)
    try:
        stdout, sterr = process.communicate()
        rc = process.returncode
        return (rc, self.FormatPipe(stdout), self.FormatPipe(stderr))
    except Exception:
        return (-1, None, None)

    # Creates process and immediately awaits tuple results

    def ProcessSync(self, command, path=""):
        try:
            process = self.ProcessAsync(command, path)
            return self.AwaitAsync(process)
        except Exception:
            return (-1, None, None)

    def DirectoryExists(self, _path):
        return os.path.exists(str(_path))

    def CreateDirectory(self, _path):
        path = str(_path)
        if self.DirectoryExists(path) == False:
            os.makedirs(path)
            os.chown(path, 5808, 5808)

    def DeleteDirectory(self, _path):
        path = str(_path)
        if self.DirectoryExists(path) == True:
            try:
                shutil.rmtree(path)
            except Exception:
                self.log.error("Experienced an exception trying to remove " + path)

    # Changes directory during "with" block and then switches back

    @contextmanager
    def ChangeDirectory(self, _path):
        path = str(_path)
        os.chdir(path)
        try:
            yield
        finally:
            os.chdir(self.pwd)


# ------------------------ Main program ------------------------

if __name__ == '__main__':
    print("--------------------------------------------------------")
    print("DEBUG (__main__): Init")

    # cwd = os.getcwd()			# current working directory
    # print(cwd)				# /tmp/rach
    # path = os.path.realpath(__file__)
    # print(path)				# /tmp/rach/mygit.py
    # dir_path = os.path.dirname(path)
    # print(dir_path)			# /tmp/rach
    # filename = os.path.basename(path)
    # print(filename)			# mygit.py
