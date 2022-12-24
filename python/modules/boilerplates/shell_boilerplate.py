#!/usr/bin/env python
"""Common logic for shell interactions"""

# --- Global Shell Commands ---
# :-Helper-:        format_resource, valid_resource, get_random_password
# JSON:             is_json_parse, is_json_str, json_parse, json_convert, json_save
# Utility:          directory_shift, directory_change, is_list_of_strings, list_differences, print_command
# Process:          process_exit, process_fail, process_id, process_parent_id
# Path:             path_current, path_expand, path_join, path_exists, path_dir, path_basename, path_filename
# Directory:        directory_list, directory_create, directory_delete, directory_copy, directory_sync
# File:             file_read, file_write, file_delete, file_rename, file_copy, file_hash, file_match, file_backup
# Signal:           signal_max, signal_handler, signal_send
# SubProcess:       subprocess_run, subprocess_log

# --- SubProcess Class Commands ---
# await_results, is_done, format_output

import distutils.dir_util
# import distutils.file_util
import json
import os
import re
import subprocess
import sys
import time
# import signal
from contextlib import contextmanager
from typing import Dict, List, Optional, Tuple

import logging_boilerplate as log

# --- Module Key ---
# subprocess        Pipe a service command like you would ad hoc
# multiprocessing   Thread multiple processes into a Pool or Queue
# socket            Communication between server/client end points

# ------------------------ Classes ------------------------

# https://goodcode.io/articles/python-dict-object
# Access dictionary items as object attributes


class _dict2obj(dict):
    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError("No such attribute: " + name)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            raise AttributeError("No such attribute: " + name)


# ------------------------ Global Shell Commands ------------------------

# --- Helper Commands ---

# Must conform to the following pattern: '^[0-9a-zA-Z-]+$'
def format_resource(raw_name: str, lowercase: Optional[bool] = True) -> str:
    """Method that formats a string name into a resource name"""
    if not (raw_name and isinstance(raw_name, str)):
        TypeError("'raw_name' parameter expected as string")
    name = raw_name.lower() if lowercase else raw_name  # lowercase
    # name = re.sub('[^a-zA-Z0-9 \n\.]', '-', raw_name) # old, ignores '.'
    name = re.sub("[^a-zA-Z0-9-]", "-", name)  # replace
    return name


# Must conform to the following pattern: '^[0-9a-zA-Z-]+$'
def valid_resource(raw_name: str, lowercase: Optional[bool] = True) -> bool:
    """Method that validates whether a resource exists"""
    og_name = str(raw_name)
    formatted_name = format_resource(raw_name, lowercase)
    return bool(og_name == formatted_name)


# https://pynative.com/python-generate-random-string
def get_random_password(length: int = 16) -> str:
    """Method that returns a randomized password"""
    import random
    import string

    # Load all lower/upper case letters, digits, and special characters
    random_source: str = string.ascii_letters + string.digits + string.punctuation
    # Guarantee at least 1 of each
    password: str = random.choice(string.ascii_lowercase)
    password += random.choice(string.ascii_uppercase)
    password += random.choice(string.digits)
    password += random.choice(string.punctuation)
    # Fill in the remaining length
    for i in range(length - 4):
        password += random.choice(random_source)
    # Randomly shuffle all the characters
    password_list: List[str] = list(password)
    random.SystemRandom().shuffle(password_list)
    password = "".join(password_list)
    return password


# --- Utility Commands ---

# Changes directory during 'with' block and then switches back
@contextmanager
def directory_shift(path):
    """Method that changes directory prior to next step"""
    if not isinstance(path, str):
        return
    working_directory = path_current()
    directory_change(path)
    try:
        yield
    finally:
        directory_change(working_directory)


def directory_change(path):
    """Method that changes directory"""
    os.chdir(path)


def is_list_of_strings(obj) -> bool:
    """Method that validates whether object is a list of strings"""
    if not isinstance(obj, list):
        return False
    # return bool(obj) and all(isinstance(elem, str) for elem in obj)
    if not obj:
        return True  # empty list
    return all(isinstance(elem, str) for elem in obj)


def list_differences(first, second):
    """Method that return items from the first list that aren't in the second list"""
    second = set(second)
    return [item for item in first if item not in second]


# Provide beginning text of command option to 'secure' and remaining will be hidden
def print_command(command: List[str], secure: Optional[str] = "") -> str:
    """Method that prints the main command text and hiding sensitive text"""
    if not (command and is_list_of_strings(command)):
        TypeError("'command' parameter expected as list of strings")
    _command: List[str] = command.copy()
    if secure:
        # Print password-safe version of command
        for (i, line) in enumerate(_command):
            if line.startswith(secure):
                _command[i] = f"{secure}*"
    display_command: str = " ".join(map(str, _command))  # using list comprehension
    _log.debug(display_command)
    return display_command


# --- Process (List State) Commands ---

def process_exit():
    """Method that exits the process"""
    sys.exit(0)


def process_fail():
    """Method that fails the process"""
    sys.exit(1)


def process_id() -> int:
    """Method that returns the process ID"""
    return os.getpid()


def process_parent_id() -> int:
    """Method that returns the parent process ID"""
    return os.getppid()


# --- Path Commands ---

def path_current() -> str:
    """Method that returns the current directory path"""
    return os.getcwd()


# Expands user directory and environmental variables
def path_expand(path: str) -> str:
    """Method that returns the absolute path"""
    result: str = os.path.expanduser(path)
    result = os.path.expandvars(result)
    result = os.path.abspath(result)
    return result


def path_join(path: str, *paths) -> str:
    """Method that returns the joined paths"""
    return os.path.join(path, *paths)


# Pass either "f" (file) or 'd' (directory) to file_type
def path_exists(path: str, file_type="") -> bool:
    """Method that validates whether the path exists"""
    path = path_expand(path)
    if not (path and isinstance(path, str)):
        raise TypeError("path_exists() expects 'path' parameter as string")
    # Use more specific type of check if provided
    if file_type == "d":
        return os.path.isdir(path)
    elif file_type == "f":
        return os.path.isfile(path)
    else:
        return os.path.exists(path)


# Returns '/foo/bar' from /foo/bar/item
def path_dir(name: str) -> str:
    """Method that returns all but the last segment of a path"""
    return os.path.dirname(name)


# Returns 'item' from /foo/bar/item
def path_basename(name: str) -> str:
    """Method that returns the last segment of a path"""
    return os.path.basename(name)


# Returns 'file.txt.zip' from /path/to/some/file.txt.zip.asc
# https://stackoverflow.com/questions/678236/how-to-get-the-filename-without-the-extension-from-a-path-in-python
def path_filename(name: str) -> str:
    """Method that returns the last file segment of a path"""
    extension_trimmed = os.path.splitext(name)[0]
    filename: str = path_basename(extension_trimmed)
    return filename


# --- Directory Commands ---

def directory_create(path: str, mode=0o775) -> List[str]:
    """Method that creates a directory"""
    directories_created: List[str] = distutils.dir_util.mkpath(path, mode)
    return directories_created


# Use directory_sync() for similar functionality with file filters
def directory_copy(src: str, dest: str) -> List[str]:
    """Method that copies a directory"""
    prefix = path_basename(src)
    full_dest = path_join(dest, prefix) if path_basename(dest) != prefix else dest
    destination_paths: List[str] = distutils.dir_util.copy_tree(src, full_dest, update=True)
    return destination_paths


def directory_delete(path: str):
    """Method that deletes a directory"""
    # result = None
    if path_exists(path, "d"):
        # Better alternative to shutil.rmtree(path)
        # result = distutils.dir_util.remove_tree(path)
        distutils.dir_util.remove_tree(path)
    # return result


def directory_list(path: str) -> List[str]:
    """Method that list a directory's contents"""
    if not path_exists(path, "d"):
        return []
    paths: List[str] = os.listdir(path)
    paths.sort()
    return paths


# Uses rsync, a better alternative to 'shutil.copytree' with ignore
def directory_sync(src: str, dest: str, recursive: Optional[bool] = True, purge: Optional[bool] = True, cut: Optional[bool] = False,
                   include=(), exclude=(), debug: Optional[bool] = False
                   ) -> Tuple[List[str], List[str]]:
    """Method that syncs a directory's contents"""
    if not isinstance(include, tuple):
        raise TypeError("directory_sync() expects 'include' parameter as tuple")
    if not isinstance(exclude, tuple):
        raise TypeError("directory_sync() expects 'exclude' parameter as tuple")
    _log.debug("Init")
    changed_files: List[str] = []
    changes_dirs: List[str] = []
    # Create sequence of command options
    command_options = []
    # --itemize-changes returns files with any change (e.g. permission attributes)
    # --list-only returns eligible files, not what actually changed
    command_options.append("--itemize-changes")
    command_options.append("--compress")
    command_options.append("--prune-empty-dirs")
    command_options.append("--human-readable")
    command_options.append("--out-format=%i %n")  # omit %L for symlink paths
    # No operations performed, returns file paths the actions would effect
    if debug:
        command_options.append("--dry-run")
    # Copy files recursively, not only first level
    if recursive:
        command_options.append("--archive")  # rlptgoD (not -H -A -X)
    else:
        command_options.append("--links")
        command_options.append("--perms")
        command_options.append("--times")
        command_options.append("--group")
        command_options.append("--owner")
        command_options.append("--devices")
        command_options.append("--specials")
    # Purge destination files not in source
    if purge:
        command_options.append("--delete")
    # Delete source files after successful transfer
    if cut:
        command_options.append("--remove-source-files")
    # Add whitelist/blacklist filters
    for i in include:
        if i:
            command_options.append(f"--include={i}")
    for i in exclude:
        if i:
            command_options.append(f"--exclude={i}")
    # Build and run the command
    command = ["rsync"]
    command.extend(command_options)
    command.extend([src, dest])
    _log.debug(f"command used: {command}")
    (stdout, stderr, rc) = subprocess_run(command)
    # subprocess_log(_log, stdout, stderr, rc)

    results: List[str] = str.splitlines(str(stdout))
    _log.debug(f"results: {results}")

    for r in results:
        result = r.split(" ", 1)
        itemized_output = result[0]
        file_name = result[1]
        if itemized_output[1] == "f":
            changed_files.append(path_join(dest, file_name))
        elif itemized_output[1] == "d":
            changes_dirs.append(path_join(dest, file_name))

    _log.debug(f"changed_files: {changed_files}")
    return (changed_files, changes_dirs)


# --- File Commands ---

# Touch file and optionally fill with content
def file_write(path: str, content=None, append=False):
    """Method that creates a file"""
    # Ensure path is specified
    if not isinstance(path, str):
        raise TypeError("file_write() expects 'path' parameter as string")
    strategy = "a" if (append) else "w"  # write mode
    # open() only accepts absolute paths, not relative
    path = path_expand(path)
    # Ensure containing directory exists
    if not path_exists(path, "d"):
        directory_create(path_dir(path))
    # http://python-notes.curiousefficiency.org/en/latest/python3/text_file_processing.html
    f = open(path, strategy, encoding="latin-1")
    # Accept content as string or sequence of strings
    if content:
        if content is None:
            f.write("")
        elif is_list_of_strings(content):
            f.writelines(content)
        else:
            f.write(str(content))
    f.close()


def file_read(path: str, oneline: Optional[bool] = False) -> str:
    """Method that reads a file's content"""
    data: str = ""
    if not (path or path_exists(path, "f")):
        return data
    try:
        path = path_expand(path)
        # Open with file() is deprecated
        # http://python-notes.curiousefficiency.org/en/latest/python3/text_file_processing.html
        f = open(path, "r", encoding="latin-1")  # default, read mode
        data = f.readline().rstrip() if (oneline) else f.read().strip()
        f.close()
    except Exception:
        data = ""
    return data


def file_delete(path: str):
    """Method that deletes a file"""
    path = path_expand(path)
    if path_exists(path, "f"):
        os.unlink(path)


def file_rename(src: str, dest: str):
    """Method that renames a file"""
    src = path_expand(src)
    dest = path_expand(dest)
    if path_exists(src, "f"):
        os.rename(src, dest)


def file_copy(src: str, dest: str) -> bool:
    """Method that copies a file"""
    if not path_exists(src, "f"):
        return False
    command = ["cp", "--force", src, dest]
    (stdout, stderr, rc) = subprocess_run(command)
    # subprocess_log(_log, stdout, stderr, rc, debug=ARGS.debug)
    return bool(rc == 0)


def file_hash(path: str) -> str:
    """Method that verifies a file hash"""
    if not path_exists(path, "f"):
        return ""
    # Using SHA-2 hash check (more secure than MD5|SHA-1)
    command: List[str] = ["sha256sum", path]
    (stdout, stderr, rc) = subprocess_run(command)
    # subprocess_log(_log, stdout, stderr, rc, debug=ARGS.debug)
    results: List[str] = str(stdout).split()
    # _log.debug(f"results: {results}")
    return results[0]


# Uses hash to validate file integrity
def file_match(path1: str, path2: str) -> bool:
    """Method that verifies whether files match based on hash"""
    # _log.debug(f"path1: {path1}")
    hash1 = file_hash(path1)
    # _log.debug(f"hash1: {hash1}")
    # _log.debug(f"path2: {path2}")
    hash2 = file_hash(path2)
    # _log.debug(f"hash2: {hash2}")
    if len(hash1) > 0 and len(hash2) > 0:
        return bool(hash1 == hash2)
    else:
        return False


def file_backup(path: str, ext="bak", time_format="%Y%m%d-%H%M%S") -> str:
    """Method that creates a file backup"""
    current_time = time.strftime(time_format)
    backup_path = f"{path}.{current_time}.{ext}"
    file_rename(path, backup_path)
    return backup_path


# --- JSON Commands ---

# https://realpython.com/python-json
def _decode_dict(dct) -> _dict2obj:
    """Method that casts dictionary items to be accessed as object attributes"""
    return _dict2obj(dct)


def is_json_parse(obj) -> bool:
    """Method that validates whether object is a JSON parse"""
    return isinstance(obj, _dict2obj)


def is_json_str(json_str: str) -> bool:
    """Method that validates whether string is JSON"""
    if not (json_str and isinstance(json_str, str)):
        return False
    results = json_parse(json_str)
    return bool(results)


# Deserialize JSON string to Python dictionary: https://docs.python.org/2/library/json.html
def json_parse(json_str: str):
    """Method that deserializes JSON string to Python dictionary"""
    results = None
    if not (json_str and isinstance(json_str, str)):
        return results
    # _log.debug("attempting json.loads")
    # _log.debug(f"json_str: {json_str}")
    try:
        results = json.loads(json_str, object_hook=_decode_dict)  # convert to dict
    except ValueError as e:
        results = ""
    # _log.debug(f"results: {results}")
    return results


# Serialize Python dictionary into JSON string
def json_convert(data: str, indent=4):
    """Method that serializes Python dictionary into JSON string"""
    results = None
    if not (data and isinstance(data, dict)):
        return results
    # _log.debug("attempting json.dumps")
    # _log.debug(f"data: {data}")
    try:
        results = json.dumps(data, indent=indent)  # convert to json
    except ValueError as e:
        results = ""
    # _log.debug(f"results: {results}")
    return results


def json_save(path: str, json_str: str, indent=4):
    """Method that saves JSON to a file"""
    if not (path and isinstance(path, str)):
        TypeError("'path' parameter expected as string")
    if not (json_str and isinstance(json_str, str)):
        TypeError("'json_str' parameter expected as string")
    if not (indent and isinstance(indent, int)):
        TypeError("'indent' parameter expected as integer")
    # Handle previous service principal if found
    if path_exists(path, "f"):
        backup_path = file_backup(path)
    # https://stackoverflow.com/questions/39491420/python-jsonexpecting-property-name-enclosed-in-double-quotes
    # Valid JSON syntax uses quotation marks; single quotes are only valid in string
    # https://stackoverflow.com/questions/43509448/building-json-file-out-of-python-objects
    file_ready = json_convert(json_str, indent)
    file_write(path, file_ready)


# --- Process Commands ---

# Creates asyncronous process and immediately awaits the tuple results
# NOTE: Only accepting 'command' as list; argument options can have spaces
def run_subprocess(
    command: List[str],
    cwd: Optional[str] = "",
    env: Optional[Dict[str, str]] = None,
) -> Tuple[str, str, int]:
    """Method that runs a command in a subprocess"""
    if not is_list_of_strings(command):
        raise TypeError("'command' parameter expected as list/sequence of strings")
    if not isinstance(cwd, str):
        raise TypeError("'cwd' parameter expected as string")
    if not (env is None or isinstance(env, dict)):
        raise TypeError("'env' parameter expected as dictionary")

    # process: SubProcess = SubProcess(command, cwd, env)
    # (stdout, stderr, rc) = process.await_results()

    # TODO: detect OS - use Powershell for Windows - use Bash for *nix
    # run_command = ["pwsh", "-Command"] + command
    run_command = ["powershell", "-Command"] + command
    _log.debug(f"run_command: {run_command}")
    # results = subprocess.run(command, universal_newlines=True, check=True, capture_output=True)
    results = subprocess.run(run_command, universal_newlines=True, check=True, capture_output=True)
    _log.debug(f"subprocess results: {results}")

    stdout: str = results.stdout
    stderr: str = results.stderr
    rc: int = results.returncode

    return (stdout, stderr, rc)


# Log the subprocess output provided
def log_subprocess(_log: log._logger_type, stdout=None, stderr=None, rc=None, debug=False):
    """Method that logs a command in a subprocess"""
    # if not is_logger(_log): raise TypeError("subprocess_log() expects '_log' parameter as logging.Logger instance")
    if isinstance(stdout, str) and len(stdout) > 0:
        log_stdout = f"stdout: {stdout}" if debug else stdout
        _log.info(log_stdout)
    if isinstance(stderr, str) and len(stderr) > 0:
        log_stderr = f"stderr: {stderr}" if debug else stderr
        # _log.error(log_stderr)
        _log.info(log_stderr)  # INFO so message is below WARN level (default on import)
    if isinstance(rc, int) and debug:
        log_rc = f"rc: {rc}" if debug else rc
        _log.debug(log_rc)

    # debug=False           debug=True
    # [Info]  "{0}"         "stdout: {0}"
    # [Info]  "{0}"         "stderr: {0}"
    # [Debug]               "rc: {0}"


# Creates asyncronous process and immediately awaits the tuple results
# NOTE: Only accepting 'command' as list; argument options can have spaces
def subprocess_run(command: List[str], path="", env=None, shell=False) -> Tuple[str, str, int]:
    """Method that runs a command in a subprocess"""
    if not is_list_of_strings(command):
        raise TypeError("'command' parameter expected as list/sequence of strings")
    if not isinstance(path, str):
        raise TypeError("'path' parameter expected as string")
    if not (env is None or isinstance(env, dict)):
        raise TypeError("'env' parameter expected as dictionary")
    if not isinstance(shell, bool):
        raise TypeError("'shell' parameter expected as boolean")
    process: SubProcess = SubProcess(command, path, env, shell)
    (stdout, stderr, rc) = process.await_results()
    return (stdout, stderr, rc)


# Log the subprocess output provided
def subprocess_log(_log: log._logger_type, stdout=None, stderr=None, rc=None, debug=False):
    """Method that logs a command in a subprocess"""
    # if not is_logger(_log): raise TypeError("subprocess_log() expects '_log' parameter as logging.Logger instance")
    if isinstance(stdout, str) and len(stdout) > 0:
        log_stdout = f"stdout: {stdout}" if debug else stdout
        _log.info(log_stdout)
    if isinstance(stderr, str) and len(stderr) > 0:
        log_stderr = f"stderr: {stderr}" if debug else stderr
        # _log.error(log_stderr)
        _log.info(log_stderr)  # INFO so message is below WARN level (default on import)
    if isinstance(rc, int) and debug:
        log_rc = f"rc: {rc}" if debug else rc
        _log.debug(log_rc)

    # debug=False           debug=True
    # [Info]  "{0}"         "stdout: {0}"
    # [Info]  "{0}"         "stderr: {0}"
    # [Debug]               "rc: {0}"


# --- Signal Commands ---

# def signal_max():
#     return int(signal.NSIG) - 1


# # Accepts 'task' of <function>, 0 (signal.SIG_DFL), or 1 (signal.SIG_IGN)
# def signal_handler(signal_num, int):
#     # Validate parameter input
#     if not isinstance(signal_num, int):
#         raise TypeError("signal_handler() expects 'signal_num' parameter as integer")
#     task_whitelist = [signal.SIG_DFL, signal.SIG_IGN]
#     valid_task = callable(task) or task in task_whitelist
#     if not valid_task:
#         raise TypeError("signal_handler() expects 'task' parameter as callable <function> or an integer of 0 or 1 (signal.SIG_DFL or signal.SIG_IGN)")
#     # Update the signal handler (callback method)
#     signal.signal(signal_num, task)


# def signal_send(pid, signal_num=signal.SIGTERM):
#     if not (pid and isinstance(pid, int)): raise TypeError("signal_send() expects 'pid' parameter as positive integer")
#     if not isinstance(signal_num, int): raise TypeError("signal_send() expects 'signal_num' parameter as integer")
#     os.kill(pid, signal_num)


# ------------------------ SubProcess Class ------------------------

# Only accepts 'command' parameter as a list/sequence of strings
# - Cannot string split because any argument options with values use spaces
class SubProcess(object):
    """Class of subprocess methods"""

    def __init__(self, command: List[str], chdir: Optional[str] = "", env: Optional[Dict[str, str]] = None, shell: Optional[bool] = False):
        if not is_list_of_strings(command):
            raise TypeError("'command' property expected as list/sequence of strings")
        if not isinstance(chdir, str):
            raise TypeError("'chdir' property expected as string")
        if not (env is None or isinstance(env, dict)):
            raise TypeError("'env' property expected as dictionary")
        if not isinstance(shell, bool):
            raise TypeError("'shell' property expected as boolean")
        # Initial values
        self.command: List[str] = command
        self.cwd: str = path_current()
        self.chdir: str = str(chdir)
        self.env = env
        self.rc: int = int()
        self.stdout: str = str()
        self.stderr: str = str()

        # Build arguments and environment variables to support command
        command_args = {
            "close_fds": True,
            "universal_newlines": True,
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE
        }

        if env or shell:
            # _log.debug("evaluating subprocess as shell")
            command_args["shell"] = True

        if env:
            # _log.debug("implementing environment variables")
            # https://stackoverflow.com/questions/2231227/python-subprocess-popen-with-a-modified-environment
            # Combine current environment variables with those provided
            current_env = os.environ.copy()
            # _log.debug(f"current_env: {current_env}")
            current_env.update(env)  # update for dict, extend for list
            # _log.debug(f"current_env: {current_env}")
            # command_args["shell"] = True
            command_args["env"] = current_env
            self.env = current_env

        # if not hasattr(command_args, "shell") or command_args["shell"] is False:
        #     # Get the windows system directory
        #     win_dir_path = os.path.join(os.environ['WINDIR'], 'System32')
        #     # Get the windows executable file ( notepad.exe ) path.
        #     cmd_executeable_file_path = os.path.join(win_dir_path, 'notepad.exe')
        #     self.command.insert(0, cmd_executeable_file_path)

        # Create an async process to await
        # https://docs.python.org/3.9/library/subprocess.html#subprocess.Popen
        process_dir: str = self.chdir if bool(self.chdir) else self.cwd
        with directory_shift(process_dir):
            self.process = subprocess.Popen(self.command, **command_args)

    # def __repr__(self):
    #     return self.process

    def __str__(self):
        return str(self.process)

    # Waits for process to finish and returns output tuple (stdout, stderr, rc)

    def await_results(self) -> Tuple[str, str, int]:
        """Method that returns process output (stdout, stderr, rc)"""
        try:
            (stdout, stderr) = self.process.communicate()
            self.rc = self.process.returncode
            self.pid = self.process.pid
            self.stdout = self.format_output(stdout)
            self.stderr = self.format_output(stderr)
            return (self.stdout, self.stderr, self.rc)
        except Exception:
            return ("", "", -1)

    # ProcessOutputFormat

    def format_output(self, text: str) -> str:
        """Method that formats process output"""
        # Split newlines and strip/trim whitespace
        whitespace_trimmed = str(text).strip()
        if not whitespace_trimmed:
            return ""
        if whitespace_trimmed.endswith("\n"):
            return whitespace_trimmed[-2]
        else:
            return whitespace_trimmed


# ------------------------ Main program ------------------------

# Initialize the logger
BASENAME: str = "shell_boilerplate"
ARGS = log.LogArgs()  # for external modules
_log: log.Logger = log.get_logger(BASENAME)

if __name__ == "__main__":
    # Returns argparse.Namespace; to pass into function, use **vars(self.ARGS)
    def parse_arguments():
        """Method that parses arguments provided"""
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--debug", action="store_true")
        parser.add_argument("--log-path", default="")
        parser.add_argument("--test", choices=["subprocess", "multiprocess", "xml"])
        return parser.parse_args()
    ARGS = parse_arguments()

    #  Configure the main logger
    LOG_HANDLERS = log.default_handlers(ARGS.debug, ARGS.log_path)
    log.set_handlers(_log, LOG_HANDLERS)

    _log.debug(f"ARGS: {ARGS}")
    _log.debug("------------------------------------------------")

    # -------- XML Test --------
    if ARGS.test == "xml":
        # Build command to send
        xml_config: str = "$HOME/configuration.xml"
        xml_schema: str = "$HOME/configuration.xsd"
        validator_command: List[str] = ["/usr/bin/xmllint", "--noout", f"--schema {xml_schema}", xml_config]
        _log.debug(f"validation command => {validator_command}")

        # Validate configuration against the schema
        (STDOUT, STDERR, RC) = subprocess_run(validator_command)
        if RC != 0:
            _log.error(f"XML file ({xml_config}) failed to validate against schema ({xml_schema})")
            subprocess_log(_log, STDOUT, STDERR, RC, debug=ARGS.debug)
        else:
            _log.debug(f"{xml_config} was successfully validated")

    # -------- SubProcess Test --------
    elif ARGS.test == "subprocess":
        test_command: List[str] = ["ls", "-la", "/var"]
        _log.debug(f"test command => {test_command}")
        (STDOUT, STDERR, RC) = subprocess_run(test_command)
        subprocess_log(_log, STDOUT, STDERR, RC, debug=ARGS.debug)

        # Test writing to files
        test_file = "/tmp/ewertz"
        test_command = ["cat", test_file]
        inputs: List[str] = ["", "123", "12345", "1"]
        for I in inputs:
            file_write(test_file, I)
            (STDOUT, STDERR, RC) = subprocess_run(test_command)
            subprocess_log(_log, STDOUT, STDERR, RC, debug=ARGS.debug)
        file_delete(test_file)

    # -------- SubProcess (simple) Test --------
    else:
        # test_command = ["ls", "-la", "/tmp"]
        # test_command = ["ls"]
        test_command = ["pwd"]
        _log.debug(f"test command => {test_command}")
        # (STDOUT, STDERR, RC) = subprocess_run(test_command)
        (STDOUT, STDERR, RC) = run_subprocess(test_command)
        subprocess_log(_log, STDOUT, STDERR, RC, debug=ARGS.debug)

    # --- Usage Example ---
    # sudo python /root/.local/lib/python2.7/site-packages/shell_boilerplate.py
    # sudo python /root/.local/lib/python2.7/site-packages/shell_boilerplate.py --debug --test=subprocess
    # py $Env:AppData\Python\Python311\site-packages\boilerplates\shell_boilerplate.py --debug --test=subprocess
