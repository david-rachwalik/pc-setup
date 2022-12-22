#!/usr/bin/env python

# Basename: mytest
# Description: Backup a directory of files
# Version: 1.0
# VersionDate: 04 Jan 2020

# Example: python $ENV:UserProfile\AppData\Roaming\Python\Python38\site-packages\mytest.py
# Example: python C:\Users\david\AppData\Roaming\Python\Python38\site-packages\mytest.py

#                   *** Options ***
# src:          Path to source files                    default=(current directory)
# dest:         Path to backup directory                default=(~/Backups)
# suffix:       Directory name or relative path end     default=(current direcory name)
# extension:    Extension file types to include         default="*"
# deep:         Copy/move files in subdirectories       default=False
# cut:          Move files instead of copy              default=False

import argparse
import os
import shutil
import sys

from shell_boilerplate import ShellManager

# ------------------------ Primary classes/functions ------------------------


class MyTest(ShellManager):
    def __init__(self):
        self.args = self.ParseCommandLineArguments()
        logLevel = 20                       # logging.INFO
        if self.args.debug:
            logLevel = 10   # logging.DEBUG
        # Initialize the inherited class constructor
        ShellManager.__init__(self, logLevel)
        self.log.debug("(MyTest:__init__) Init")
        # Initial values
        self.args.src = self.ExpandPath(self.args.src)
        self.log.debug("(MyTest:__init__) src {0}".format(self.args.src))
        # self.args.dest = os.path.join(self.ExpandPath(self.args.dest), self.args.suffix)

        # self.args.dest = self.ExpandPath(self.args.dest)
        # dest_basepath = os.path.basename(self.args.dest)
        # # Add suffix to path when the top directory name doesn't match
        # if self.args.dest != os.path.join(dest_basepath, self.args.suffix):
        #     self.log.info(dest_basepath)
        #     self.log.info(self.args.suffix)
        #     self.args.dest = os.path.join(self.ExpandPath(self.args.dest), self.args.suffix)
        # else:
        #     self.log.info(self.args.dest)

        # # ---------------- Primary business logic area ----------------
        # self.log.debug("source: {0}".format(self.args.src))
        # self.log.debug("destination: {0}".format(self.args.dest))

        # # Ensure source directory exists
        # if not os.path.isdir(self.args.src):
        #     self.log.error("Source directory does not exist")
        #     self.Fail()
        # # Ensure backup directory exists; will create if absent
        # self.DirectoryCreate(self.args.dest)
        # # Perform backup copy of directory files
        # self.DirectoryCopy(self.args.src, self.args.dest, self.args.deep, self.args.cut, self.args.extension)

        command = "ls"
        process = self.ProcessAsync(command)
        (rc, stdout, stderr) = self.ProcessAwaitAsync(process)
        self.log.info("(MyTest:__init__) rc: {0}".format(rc))
        self.log.info("(MyTest:__init__) stdout: {0}".format(stdout))
        self.log.info("(MyTest:__init__) stderr: {0}".format(stderr))

    def ParseCommandLineArguments(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--src", default=os.getcwd())
        parser.add_argument("--dest", default="$HOME/Backups")
        parser.add_argument("--suffix", default=os.path.basename(os.getcwd()))
        parser.add_argument("--debug", action="store_true")
        parser.add_argument("--extension", default="*")
        parser.add_argument("--deep", action="store_true")
        parser.add_argument("--cut", action="store_true")
        return parser.parse_args()


# ------------------------ Main Program ------------------------

if __name__ == '__main__':
    backup = MyTest()
    backup.Exit()
