#!/usr/bin/env python

# Basename: shell_boilerplate
# Description: Common business logic for *nix shell interactions
# Version: 1.5
# VersionDate: 27 Feb 2020

# --- Global Shell Commands ---
# Utility:          directory_shift, directory_change, is_list_of_strings, list_differences
# Process:          process_exit, process_fail, process_id, process_parent_id
# Path:             path_current, path_expand, path_join, path_basename, path_filename, path_exists
# Directory:        directory_list, directory_create, directory_delete, directory_copy, directory_sync
# File:             file_read, file_write, file_delete
# Signal:           signal_max, signal_handler, signal_send
# SubProcess:       subprocess_await, subprocess_print
# --- SubProcess Class Commands ---
# await_results, is_done, format_output

from logging_boilerplate import LogManager
import sys, os, subprocess, signal
from contextlib import contextmanager
import distutils.dir_util
# import distutils.file_util

# --- Module Key ---
# subprocess        Pipe a service command like you would ad hoc
# multiprocessing   Thread multiple processes into a Pool or Queue
# socket            Communication between server/client end points

try:
    # Python 2 has both 'str' (bytes) and 'unicode' text
    basestring = basestring
    unicode = unicode
except NameError:
    # Python 3 names the unicode data type 'str'
    basestring = str
    unicode = str

# ------------------------ Global Shell Commands ------------------------

# --- Utility Commands ---

# Changes directory during 'with' block and then switches back
@contextmanager
def directory_shift(path):
    if not isinstance(path, str): return
    working_directory = path_current()
    directory_change(path)
    try:
        yield
    finally:
        directory_change(working_directory)


def directory_change(path):
    os.chdir(path)


def is_list_of_strings(obj):
    if not isinstance(obj, list): return False
    return bool(obj) and all(isinstance(elem, str) for elem in obj)


# Return items from first list that aren't in second
def list_differences(first, second):
    second = set(second)
    return [item for item in first if item not in second]


# --- Process (List State) Commands ---

def process_exit():
    sys.exit(0)


def process_fail():
    sys.exit(1)


def process_id():
    return os.getpid()


def process_parent_id():
    return os.getppid()


# --- Path Commands ---

def path_current():
    return os.getcwd()


# Expands user directory and environmental variables
def path_expand(path):
    result = os.path.expanduser(path)
    result = os.path.expandvars(result)
    result = os.path.abspath(result)
    return result


def path_join(path, *paths):
    return os.path.join(path, *paths)


# Returns 'item' from /foo/bar/item
def path_basename(name):
    return os.path.basename(name)


# Returns 'file.txt.zip' from /path/to/some/file.txt.zip.asc
# https://stackoverflow.com/questions/678236/how-to-get-the-filename-without-the-extension-from-a-path-in-python
def path_filename(name):
    extension_trimmed = os.path.splitext(name)[0]
    filename = path_basename(extension_trimmed)
    return filename


# Returns '/foo/bar' from /foo/bar/item
def path_dirname(name):
    return os.path.dirname(name)


# Pass either 'f' (file) or 'd' (directory) to file_type
def path_exists(path, file_type=""):
    if not (path and isinstance(path, str)): raise TypeError("path_exists() expects 'path' parameter as string.")
    if file_type == "d":
        return os.path.isdir(path)
    elif file_type == "f":
        return os.path.isfile(path)
    else:
        return os.path.exists(path)


# --- Directory Commands ---

def directory_create(path, mode=0o775):
    directories_created = distutils.dir_util.mkpath(path, mode)
    return directories_created


# Use directory_sync() for similar functionality with file filters
def directory_copy(src, dest):
    prefix = path_basename(src)
    full_dest = path_join(dest, prefix) if path_basename(dest) != prefix else dest
    destination_paths = distutils.dir_util.copy_tree(src, full_dest, update=True)
    return destination_paths


def directory_delete(path):
    result = None
    if path_exists(path, 'd'):
        # Better alternative to shutil.rmtree(path)
        result = distutils.dir_util.remove_tree(path)
        return result


def directory_list(path):
    if not path_exists(path, 'd'): return []
    paths = os.listdir(path)
    paths.sort()
    return paths


# Uses rsync, a better alternative to 'shutil.copytree' with ignore
def directory_sync(src, dest, recursive=True, purge=True, cut=False, include=(), exclude=(), debug=False):
    if not isinstance(include, tuple): raise TypeError("directory_sync() expects 'include' parameter as tuple.")
    if not isinstance(exclude, tuple): raise TypeError("directory_sync() expects 'exclude' parameter as tuple.")
    logger.debug("(directory_sync): Init")
    changed_files = []
    changes_dirs = []
    # Create sequence of command options
    commandOptions = []
    # --itemize-changes returns files with any change (e.g. permission attributes)
    # --list-only returns eligible files, not what actually changed
    commandOptions.append("--itemize-changes")
    commandOptions.append("--compress")
    commandOptions.append("--prune-empty-dirs")
    commandOptions.append("--human-readable")
    commandOptions.append("--out-format=%i %n") # omit %L for symlink paths
    # No operations performed, returns file paths the actions would effect
    if debug: commandOptions.append("--dry-run")
    # Copy files recursively, not only first level
    if recursive:
        commandOptions.append("--archive") # rlptgoD (not -H -A -X)
    else:
        commandOptions.append("--links")
        commandOptions.append("--perms")
        commandOptions.append("--times")
        commandOptions.append("--group")
        commandOptions.append("--owner")
        commandOptions.append("--devices")
        commandOptions.append("--specials")
    # Purge destination files not in source
    if purge: commandOptions.append("--delete")
    # Delete source files after successful transfer
    if cut: commandOptions.append("--remove-source-files")
    # Add whitelist/blacklist filters
    for i in include:
        if i: commandOptions.append("--include={0}".format(i))
    for i in exclude:
        if i: commandOptions.append("--exclude={0}".format(i))
    # Build and run the command
    command = ["rsync"]
    command.extend(commandOptions)
    command.extend([src, dest])
    logger.debug("(directory_sync) command used: {0}".format(command))
    (rc, stdout, stderr) = subprocess_await(command)
    # subprocess_print(rc, stdout, stderr)

    results = str.splitlines(stdout)
    logger.debug("(directory_sync) results: {0}".format(results))

    for r in results:
        result = r.split(" ", 1)
        itemized_output = result[0]
        file_name = result[1]
        if itemized_output[1] == "f":
            changed_files.append(path_join(dest, file_name))
        elif itemized_output[1] == "d":
            changes_dirs.append(path_join(dest, file_name))

    logger.debug("(directory_sync) changed_files: {0}".format(changed_files))
    return (changed_files, changes_dirs)


# --- File Commands ---
def file_write(path, content=None, append=False):
    # Ensure path is specified
    if not isinstance(path, str): raise TypeError("file_write() expects 'path' parameter as string.")
    # Touch file and optionally fill with content
    strategy = "a" if (append) else "w"
    f = open(path, strategy)
    # Accept content as string or sequence of strings
    if content:
        if content is None:
            f.write("")
        elif is_list_of_strings(content):
            f.writelines(content)
        else:
            f.write(str(content))
    f.close()


def file_read(path, oneline=False):
    data = ""
    if not (path or path_exists(path, 'f')): return data
    try:
        # Open file; never use deprecated file()
        f = open(path, "r")
        data = f.readline().rstrip() if (oneline) else f.read().strip()
        f.close()
    except:
        data = ""
    return data


def file_delete(file):
    if path_exists(file, 'f'): os.unlink(file)


# --- Process Commands ---

# Creates asyncronous process and immediately awaits the tuple results
# NOTE: Only accepting 'command' as list; argument options can have spaces
def subprocess_await(command, path="", env="", stdout_log=None, stderr_log=None):
    process = SubProcess(command, path, env)
    (rc, stdout, stderr) = process.await_results()
    if int(rc) != 0 and is_logger(stderr_log):
        subprocess_print(stderr_log, rc, stdout, stderr, command)
    elif is_logger(stdout_log):
        subprocess_print(stdout_log, rc, stdout, stderr, command)
    return (rc, stdout, stderr)


def subprocess_print(logger, rc, stdout, stderr, prefix=""):
    # Ensure logger is provided
    if not is_logger(logger): raise TypeError("subprocess_print() expects 'logger' parameter as logger instance.")
    if prefix: prefix = "({0}) ".format(prefix)
    if int(rc) != 0:
        if stdout: logger.warning("{0}{1}".format(prefix, stdout))
        if stderr: logger.error("{0}{1}".format(prefix, stderr))
    else:
        if stdout: logger.info("{0}{1}".format(prefix, stdout))


# --- Signal Commands ---

def signal_max():
    return int(signal.NSIG) - 1


# Accepts 'task' of <function>, 0 (signal.SIG_DFL), or 1 (signal.SIG_IGN)
def signal_handler(signal_num, int):
    # Validate parameter input
    if not isinstance(signal_num, int):
        raise TypeError("signal_handler() expects 'signal_num' parameter as integer.")
    task_whitelist = [signal.SIG_DFL, signal.SIG_IGN]
    valid_task = callable(task) or task in task_whitelist
    if not valid_task:
        raise TypeError("signal_handler() expects 'task' parameter as callable <function> or an integer of 0 or 1 (signal.SIG_DFL or signal.SIG_IGN).")
    # Update the signal handler (callback method)
    signal.signal(signal_num, task)


def signal_send(pid, signal_num=signal.SIGTERM):
    if not (pid and isinstance(pid, int)): raise TypeError("signal_send() expects 'pid' parameter as positive integer.")
    if not isinstance(signal_num, int): raise TypeError("signal_send() expects 'signal_num' parameter as integer.")
    os.kill(pid, signal_num)


# --- SubProcess Class ---

# Only accepts 'command' parameter as a list/sequence of strings
# - Cannot string split because any argument options with values use spaces
class SubProcess(object):
    def __init__(self, command, path="", env=None):
        # Initial values
        self.rc = int()
        self.stdout = str()
        self.stderr = str()
        self.command = []
        self.path = str(path)
        self.env = env

        # Ensure command was provided as text or a sequence/list
        if is_list_of_strings(command):
            self.command = command
        else:
            raise TypeError("SubProcess 'command' property expects a list/sequence of strings.")

        # Build arguments and environment variables to support command
        command_args = {
            "close_fds": True,
            "universal_newlines": True,
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE
        }
        if self.env: command_args["env"] = self.env

        # Create an async process to await
        self.process = None
        if self.path:
            with directory_shift(self.path):
                self.process = subprocess.Popen(self.command, **command_args)
        else:
            self.process = subprocess.Popen(self.command, **command_args)


    # def __repr__(self):
    #     return self.process


    def __str__(self):
        return str(self.process)


    # Waits for process to finish and returns output tuple (rc, stdout, stderr)
    def await_results(self):
        try:
            (stdout, stderr) = self.process.communicate()
            self.rc = self.process.returncode
            self.pid = self.process.pid
            self.stdout = self.format_output(stdout)
            self.stderr = self.format_output(stderr)
            return (self.rc, self.stdout, self.stderr)
        except:
            return (-1, None, None)


    # ProcessOutputFormat
    def format_output(self, text):
        # Split newlines and strip/trim whitespace
        whitespace_trimmed = str(text).strip()
        if not whitespace_trimmed: return ""
        if whitespace_trimmed.endswith("\n"):
            return whitespace_trimmed[-2]
        else:
            return whitespace_trimmed


# ------------------------ Main program ------------------------

# Initialize the logger
basename = "shell_boilerplate"
log_options = LogOptions(basename)
logger = get_logger(log_options)

if __name__ == "__main__":
    # Returns argparse.Namespace; to pass into function, use **vars(self.args)
    def parse_arguments():
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--debug", action="store_true")
        parser.add_argument("--test", choices=["subprocess", "multiprocess", "xml"])
        return parser.parse_args()
    args = parse_arguments

    # Configure the logger
    log_level = 20                  # logging.INFO
    if args.debug: log_level = 10   # logging.DEBUG
    logger.setLevel(log_level)
    logger.debug("(__main__): args: {0}".format(args))
    logger.debug("(__main__): ------------------------------------------------")

    # -------- XML Test --------
    if args.test == "xml":
        # Build command to send
        xmlPath = "$HOME/configuration.xml"
        schemaPath = "$HOME/configuration.xsd"

        # validatorCmd = "/usr/bin/xmllint --noout --schema {0} {1}".format(schemaPath, xmlPath)
        validatorCmd = ["/usr/bin/xmllint", "--noout", "--schema {0}".format(schemaPath), xmlPath]
        logger.debug("(__main__): Validation command: {0}".format(validatorCmd))

        # Validate configuration against the schema
        # (rc, stdout, stderr) = subprocess_await(validatorCmd, stdout_log=logger, stderr_log=logger)
        (rc, stdout, stderr) = subprocess_await(validatorCmd)
        if rc != 0:
            logger.error("(__main__): XML file ({0}) failed to validate against schema ({1})".format(config_xml, config_xsd))
            subprocess_print(rc, stdout, stderr, validatorCmd)
        else:
            logger.debug("(__main__): {0} was successfully validated.".format(xmlPath))

    # -------- SubProcess Test --------
    elif args.test == "subprocess":
        # testCmd = "ls -la /var"
        testCmd = ["ls", "-la", "/var"]
        logger.debug("(__main__): test command: {0}".format(testCmd))
        (rc, stdout, stderr) = subprocess_await(testCmd, stdout_log=logger, stderr_log=logger)

        # Test writing to files
        testFile = "/tmp/ewertz"
        # testCommand = "cat {0}".format(testFile)
        testCommand = ["cat", testFile]
        inputs = ["", "123", "12345", "1"]
        for i in inputs:
            file_write(testFile, i)
            (rc, stdout, stderr) = subprocess_await(testCommand, stdout_log=logger, stderr_log=logger)
        file_delete(testFile)

    # -------- SubProcess (simple) Test --------
    else:
        testCmd = ["ls", "-la", "/tmp"]
        logger.debug("(__main__): test command: {0}".format(testCmd))
        (rc, stdout, stderr) = subprocess_await(testCmd, stdout_log=logger, stderr_log=logger)


    # --- Usage Example ---
    # sudo python /root/.local/lib/python2.7/site-packages/shell_boilerplate.py
    # sudo python /root/.local/lib/python2.7/site-packages/shell_boilerplate.py --debug --test=subprocess
