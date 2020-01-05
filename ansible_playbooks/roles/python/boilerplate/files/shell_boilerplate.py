#!/usr/bin/env python3

# Basename: shell_boilerplate
# Description: Common logic for *nix shell interactions
# Version: 0.6
# VersionDate: 16 Dec 2019

from logging_boilerplate import LogManager
import shlex, subprocess
import sys, os, shutil, stat
from contextlib import contextmanager
import distutils.dir_util, distutils.file_util

# ------------------------ Classes ------------------------

class ShellManager(object):
    def __init__(self, logLevel=20):
        # Initialize the inherited class constructor
        LogManager.__init__(self, logLevel)
        self.log.debug("(ShellManager:__init__) Init")


    def Exit(self):
        self.log.debug("(ShellManager:Exit) Init")
        sys.exit(0)

    
    def Fail(self):
        self.log.debug("(ShellManager:Fail) Init")
        sys.exit(1)


    def ProcessOutputFormat(self, text):
        self.log.debug("(ShellManager:ProcessOutputFormat) Init")
        # Split newlines and strip/trim whitespace
        whitespaceTrimmed = str(text).strip()
        if len(whitespaceTrimmed) == 0: return ""
        if whitespaceTrimmed.endswith("\n"):
            return whitespaceTrimmed[-2]
        else:
            return whitespaceTrimmed


    # Creates and returns an async process to await
    def ProcessAsync(self, _command, _path=""):
        self.log.debug("(ShellManager:ProcessAsync) Init")
        path = str(_path)
        # Ensure commands are provided as a sequence/list
        if isinstance(_command, list):
            command = _command
        elif isinstance(_command, str):
            command = shlex.split(_command)
        else:
            return None

        if path:
            with self.DirectoryShift(path):
                try:
                    return subprocess.Popen(command, close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                except:
                    return None
        else:
            try:
                return subprocess.Popen(command, close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except:
                return None


    # Waits for process to finish and returns output tuple (rc, stdout, stderr)
    def ProcessAwaitAsync(self, process):
        self.log.debug("(ShellManager:ProcessAwaitAsync) Init")
        try:
            stdout, stderr = process.communicate()
            rc = process.returncode
            return (rc, self.ProcessOutputFormat(stdout), self.ProcessOutputFormat(stderr))
        except:
            return (-1, None, None)


    # Creates process and immediately awaits tuple results
    def ProcessSync(self, command, path=""):
        self.loog.debug("(ShellManager:ProcessSync) Init")
        try:
            process = self.ProcessAsync(command, path)
            return self.ProcessAwaitAsync(process)
        except:
            return (-1, None, None)


    # Expands user directory and environmental variables
    def ExpandPath(self, path):
        self.log.debug("(ShellManager:ExpandPath) Init")
        result = os.path.expanduser(path)
        result = os.path.expandvars(result)
        result = os.path.abspath(result)
        return result


    # Changes directory during "with" block and then switches back
    @contextmanager
    def DirectoryShift(self, _path):
        self.log.debug("(ShellManager:DirectoryShift) Init")
        pwd = os.getcwd()
        path = str(_path)
        os.chdir(path)
        try:
            yield
        finally:
            os.chdir(pwd)


    # Providing an extension will return all files matching the extension filter specified
    # - Using value 'dir' will return all directories found
    def DirectoryFileList(self, path, extension="*"):
        self.log.debug("(ShellManager:DirectoryFileList) Init")
        results = []
        # Ensure the container directory exists
        if not os.path.isdir(path): return results

        # Gather all file names in directory
        for filename in os.listdir(path):
            filename = os.path.join(path, filename)
            # Filter to only files/directories
            if extension == "dir":
                if not os.path.isdir(filepath): continue
            else:
                if not os.path.isfile(filepath): continue
                # Filter to extension type when providing
                if extension != "*" and not filename.endswith(extension): continue
            # Save the filename of match
            results.append(filename)

        results.sort()
        filetype_text = "Directories" if (extension == "dir") else "Files"
        self.log.debug("(ShellManager:DirectoryFileList) {2} in {0}: {1}".format(path, results, filetype_text))
        return results


    def DirectoryCreate(self, path, mode=0o755):
        self.log.debug("(ShellManager:DirectoryCreate) Init")
        created_directories = distutils.dir_util.mkpath(path, mode)
        if len(created_directories) > 0:
            self.log.info("Successfully created directory {0}".format(path))


    def DirectoryDelete(self, _path):
        self.log.debug("(ShellManager:DirectoryDelete) Init")
        path = str(_path)
        if os.path.isdir(path):
            try:
                shutil.rmtree(path)
            except:
                self.log.error("Experienced an exception trying to remove {0}".format(path))


    # Update=True makes src copy to dest when it doesn't exist or is older than src
    def DirectoryCopy(self, src, dest, deep=False, cut=False, extension="*"):
        self.log.debug("(ShellManager:DirectoryCopy) Init")
        destination_paths = []
        # Toggle for recursive copy
        if deep:
            destination_paths = distutils.dir_util.copy_tree(src, dest, update=True, dry_run=True)
        elif cut:
            source_filenames = self.DirectoryFileList(src, extension)
            for filename in source_filenames:
                result = distutils.file_util.move_file(
                    os.path.join(src, filename),
                    os.path.join(dest, filename),
                    dry_run=True
                )
        else:
            # Fine source/destination directory files
            source_filenames = self.DirectoryFileList(src, extension)
            # source_directories = self.DirectoryFileList(src, "dir")
            # destination_filenames = self.DirectoryFileList(dest, extension)
            # destination_directories = self.DirectoryFileList(dest, "dir")
            for filename in source_filenames:
                result = distutils.file_util.copy_file(
                    os.path.join(src, filename),
                    os.path.join(dest, filename),
                    update=True,
                    dry_run=True
                )
                if result[1]: destination_paths.append(result[0]) # Note changes

        self.log.debug("(ShellManager:DirectoryCopy) Files copied: {0}".format(destination_paths))
