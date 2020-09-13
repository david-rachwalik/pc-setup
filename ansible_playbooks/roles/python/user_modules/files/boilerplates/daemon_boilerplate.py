#!/usr/bin/env python

# Basename: daemon_boilerplate
# Description: Common business logic for daemons
# Version: 0.6.1
# VersionDate: 23 Jul 2020

from logging_boilerplate import *
import shell_boilerplate as sh
import sys, os, time, atexit
import signal, resource, errno

try:
    # Python 2 has both 'str' (bytes) and 'unicode' text
    basestring = basestring
    unicode = unicode
except NameError:
    # Python 3 names the unicode data type 'str'
    basestring = str
    unicode = str

# ------------------------ Classes ------------------------

# Context for turning a program into daemon process instance
# Usage: subclass DaemonContext() and override the run() method
class DaemonContext(object):
    def __init__(self, basename, log_file=""):
        if not isinstance(basename, str): raise TypeError("DaemonContext() expects 'basename' parameter as string.")
        logger.debug("(DaemonContext:__init__): Init")
        # Initial values
        self.basename = basename
        self.log_file = log_file
        self.pidfile = "/var/run/{0}.pid".format(self.basename)
        self.lockfile = "/var/lock/subsys/{0}".format(self.basename)
        self._is_open = bool()


    # Entry point for 'with' context
    def __enter__(self):
        self.open()
        return self


    # Exit point for 'with' context
    def __exit__(self):
        self.close()


    @property
    def is_locked(self):
        result = sh.path_exists(self.lockfile, "f")
        return result


    @property
    def is_open(self):
        return self._is_open


    def open(self):
        logger.debug("(DaemonContext:open): Init")
        if self.is_locked:
            logger.warning("Cannot open DaemonContext instance '{0}', lockfile already exists".format(self.basename))
            return
        if self.is_open:
            logger.warning("DaemonContext instance '{0}' is open already".format(self.basename))
            return

        # ------------------------ Initial Values ------------------------
        self.working_directory = "/"
        self.umask = 0o000
        self.gid = os.getgid()
        self.uid = os.getuid()
        # Initial file descriptor values
        self.open_fds = self.list_open_file_descriptors()
        self.standard_streams = [sys.stdin, sys.stdout, sys.stderr]
        self.standard_fds = list(int(stream.fileno()) for stream in self.standard_streams)
        logger.debug("(DaemonContext:open): standard file descriptors: {0}".format(self.standard_fds))
        self.log_fds = self.find_log_file_descriptors()
        logger.debug("(DaemonContext:open): logging file descriptors: {0}".format(self.log_fds))
        # Check if log_fd is borrowing a standard index (possible error no longer occurs)
        for fd in self.log_fds:
            if fd in self.standard_fds:
                log_index = self.standard_fds.index(fd)
                self.standard_streams.pop(log_index)
                self.standard_fds.pop(log_index)
                logger.debug("(DaemonContext:open): log using standard file descriptor; adjusted standard_fds: {0}".format(self.standard_fds))
        # -------------------------------------------------------------

        # Prevent this process from generating a core dump
        self.prevent_core_dump()
        # Change file creation mask for this process
        os.umask(self.umask)
        # Change working directory of this process
        os.chdir(self.working_directory)
        # Change process owner GID and UID (in that order to avoid permission errors)
        os.setgid(self.gid)
        os.setuid(self.uid)
        # Fork the program to daemonize its context
        self.detach_process_context()
        # Reset signal behavior for daemon context; use run() for further signal updates
        self.reset_signal_handlers()
        # Reset file descriptors; automatically exclude standard I/O and log
        fd_exclusions = self.list_default_file_descriptors()
        self.close_all_open_files(exclude=fd_exclusions)
        # Redirect standard file decsriptors from /dev/pts/* to /dev/null
        for stream in self.standard_streams:
            self.redirect_stream(stream)
        logger.debug("(DaemonContext:open): standard file descriptors redirected to null: {0}".format(self.standard_fds))
        # Attach exit event
        atexit.register(self.exit_handler)
        logger.debug("(DaemonContext:open): exit handler registered")
        # Enforce unique daemon instance and store PID for stop method
        self.create_pidfile()
        self.create_lock()
        self._is_open = True
        logger.debug("(DaemonContext:open): daemon has been started")
        # Run tasks within the daemon context
        self.run()


    def close(self):
        logger.debug("(DaemonContext:close): Init")
        pid = self.read_pidfile()
        if not pid:
            logger.debug("(DaemonContext:close): pidfile '{0}' does not exist. Daemon not running?".format(self.pidfile))
            return # Not an error in a restart
        logger.debug("(DaemonContext:close): found '{0}' in pidfile".format(self.pidfile))
        # Try killing the daemon process
        try:
            while True:
                # Send terminate signal to the process
                sh.signal_send(pid)
                time.sleep(0.1)
            except OSError as exc:
                if exc.errno == errno.ESRCH:
                    # Expected to land here for graceful exit when SIGTERM takes effect
                    logger.debug("(DaemonContext:close): daemon has stopped")
                    pass # [Errno 3] no such process
                else:
                    logger.warning("(DaemonContext:close): error occurred attempting to terminate process ({0}): {exc}".format(pid, exc=exc))
                    raise
        
    
    # Write the latest PID to file
    def create_pidfile(self):
        logger.debug("(DaemonContext:create_pidfile): Init")
        sh.file_write(self.pidfile, str(sh.process_id()))
        logger.debug("(DaemonContext:create_pidfile): pid file created successfully")

    
    # Obtain an exclusive lock before running actions
    def create_lock(self):
        logger.debug("(DaemonContext:create_lock): Init")
        sh.file_write(self.lockfile)
        logger.debug("(DaemonContext:create_lock): lockfile created successfully")

    
    def read_pidfile(self):
        logger.debug("(DaemonContext:read_pidfile): Init")
        pid = sh.file_read(self.pidfile, True)
        return int(pid) if (pid) else pid

    
    def prevent_core_dump(self):
        logger.debug("(DaemonContext:prevent_core_dump): Init")
        core_resource = resource.RLIMIT_CORE
        # Ensure the resource limit exists on this platform, by requesting its current value
        try:
            resource.getrlimit(core_resource)
        except Exception as exc:
            logger.error("(DaemonContext:prevent_core_dump): System does not support RLIMIT_CORE resource limit ({exc})".format(exc=exc))
            raise
        # Set hard and soft limits to zero, i.e. no core dump at all
        core_limit = (0, 0)
        resource.setrlimit(core_resource, core_limit)


    def detach_process_context(self):
        logger.debug("(DaemonContext:detach_process_context): Init")
        self.become_child_process(error_message="Failed first fork")
        # logger.debug("(DaemonContext:detach_process_context): fork 1 pid: {0}".format(sh.process_id()))
        os.setsid() # decouple from parent
        # Do the UNIX double-fork to prevent daemon from acquiring TTY
        self.become_child_process(error_message="Failed second fork")
        # logger.debug("(DaemonContext:detach_process_context): fork 2 pid: {0}".format(sh.process_id()))
        self.pid = sh.process_id()
        logger.debug("(DaemonContext:detach_process_context): Daemon PID: {0}".format(self.pid))


    # Attempt to spawn a child process
    def become_child_process(self, error_message=""):
        logger.debug("(DaemonContext:become_child_process): Init")
        try:
            child_pid = os.fork()
        except OSError as exc:
            logger.debug("(DaemonContext:become_child_process): ERRNO {0}: {1}".format(e.errno, e.strerror))
            logger.debug("(DaemonContext:become_child_process): {message}: [{exc.errno:d}] {exc.strerror}".format(message=error_message, exc=exc))
            raise
        # Positive PID is parent process needing to exit; child process waits for parent to complete
        if child_pid > 0:
            logger.debug("(DaemonContext:become_child_process): child spawned ({0}), performing exit".format(child_pid))
            os._exit(0)
        elif child_pid == 0:
            # Wait until parent exits and child is inherited by init (PID=1) for ownership of files
            while sh.process_parent_id() != 1:
                logger.debug("(DaemonContext:become_child_process): waiting until parent ({0}) exits".format(sh.process_parent_id()))
                time.sleep(0.1)
    

    def reset_signal_handlers(self):
        logger.debug("(DaemonContext:reset_signal_handlers): Init")
        # Create signal handler map of default actions
        # NOTE: Setting signal.SIG_DFL on signal.SIGTERM is immediate exit; won't call atexit
        signal_handler_map = {
            signal.SIGUP: signal.SIG_IGN,
            signal.SIGTERM: self.terminate,
            signal.SIGTSTP: signal.SIG_IGN,
            signal.SIGTTIN: signal.SIG_IGN,
            signal.SIGTTOU: signal.SIG_IGN
        }
        logger.debug("(DaemonContext:reset_signal_handlers): signal_handler_map: {0}".format(signal_handler_map))
        # Update each signal handler (callback method)
        for (signal_number, handler) in signal_handler_map.items():
            signal.signal(signal_number, handler)
        logger.debug("(DaemonContext:reset_signal_handlers): all signal handlers are updated")
    

    # Gather open file descriptors from system directory
    def list_open_file_descriptors(self):
        logger.debug("(DaemonContext:list_open_file_descriptors): Init")
        # NOTE: Always reflects file descriptors when process was started (even with /proc/{pid}/fd)
        open_fd_strings = os.listdir("/proc/self/fd")
        open_fds = list(int(result) for result in open_fd_strings)
        logger.debug("(DaemonContext:list_open_file_descriptors): file descriptors open: {0}".format(open_fds))
        return open_fds


    def redirect_stream(self, system_stream, target_stream=None):
        # logger.debug("(DaemonContext:redirect_stream): Init")
        if target_stream is None:
            target_fd = os.open(os.devnull, os.O_RDWR)
        else:
            target_fd = target_stream.fileno()
        system_fd = system_stream.fileno()
        # Redirect a system stream to specified file
        if target_stream:
            logger.debug("(DaemonContext:redirect_stream): redirecting file descriptor {0} to {1}".format(target_fd, system_fd))
        try:
            os.dup2(target_fd, system_fd)
        except Exception as exc:
            logger.error("(DaemonContext:redirect_stream): Unable to redirect file descriptor ({exc})".format(exc=exc))
            raise
        # Cleanup '/dev/null' file when opened
        if target_stream is None:
            self.close_file_descriptor(target_fd)


    def get_file_descriptor_path(self, fd):
        # logger.debug("(DaemonContext:get_file_descriptor_path): Init")
        try:
            fd_path = os.readlink("/proc/self/fd/{0}".format(fd))
        except OSError as exc:
            if exc.errno == errno.ENOENT:
                # [Errno 2] No such file or directory
                fd_path = ""
            else:
                logger.debug("(DaemonContext:get_file_descriptor_path): Failed to get file descriptor ({0}) path: {exc}".format(fd, exc=exc))
                raise
        return fd_path


    def find_log_file_descriptors(self):
        logger.debug("(DaemonContext:find_log_file_descriptors): Init")
        log_fds = []
        for fd in self.open_fds:
            fd_path = self.get_file_descriptor_path(fd)
            if fd_path == self.log_file:
                log_fds.append(fd)
        return log_fds


    def list_default_file_descriptors(self):
        logger.debug("(DaemonContext:list_default_file_descriptors): Init")
        default_fds = []
        # Add all standard file descriptors
        for fd in self.standard_fds: default_fds.append(fd)
        # Add logging file descriptor
        for fd in self.log_fds: default_fds.append(fd)
        logger.debug("(DaemonContext:list_default_file_descriptors): default_fds: {0}".format(default_fds))
        return default_fds
        

    def close_file_descriptor(self, fd):
        logger.debug("(DaemonContext:close_file_descriptor): Init")
        if not (fd and isinstance(fd, int)): raise TypeError("(DaemonContext:close_file_descriptor) expects 'fd' parameter as positive integer.")
        try:
            os.close(fd)
        except OSError as exc:
            if exc.errno == errno.EBADF:
                pass # [Errno 9] Bad file descriptor
            else:
                logger.debug("(DaemonContext:close_file_descriptor): error closing file descriptor ({0}): {exc}".format(fd, exc=exc))
                raise
    

    # Close all open file streams; primarily needs to close /dev/tty
    def close_all_open_files(self, exclude=set()):
        logger.debug("(DaemonContext:close_all_open_files): Init")
        if not (isinstance(exclude, list) or isinstance(exclude, set)): raise TypeError("(DaemonContext:close_all_open_files) expects 'exclude' parameter as list/set.")
        logger.debug("(DaemonContext:close_all_open_files): excluded file descriptors: {0}".format(exclude))
        # Determine candidate file descriptors to close
        fds_to_close = sh.list_differences(self.open_fds, exclude)
        # Close each file descriptor
        for fd in reversed(fds_to_close):
            fd_path = self.get_file_descriptor_path(fd)
            logger.debug("(DaemonContext:close_all_open_files): closing file descriptor ({0}) for path '{1}'".format(fd, fd_path))
            self.close_file_descriptor(fd)
        logger.debug("(DaemonContext:close_all_open_files): all file descriptors are closed")


    # Cleanup lockfile and PID file
    def exit_handler(self):
        logger.debug("(DaemonContext:exit_handler): Init")
        if sh.path_exists(self.lockfile, "f"):
            logger.debug("(DaemonContext:exit_handler): removed lockfile: {0}".format(self.lockfile))
            sh.file_delete(self.lockfile)
        if sh.path_exists(self.pidfile, "f"):
            logger.debug("(DaemonContext:exit_handler): removed PID file: {0}".format(self.pidfile))
            sh.file_delete(self.pidfile)


    def run(self):
        logger.warning("(DaemonContext:run): Override this method when you subclass DaemonContext.  It will be called after the process has been daemonized.")


    def terminate(self):
        logger.warning("(DaemonContext:terminate): Signal handler for end-process")
        sh.process_exit()


# ------------------------ Main Program ------------------------

# Initialize the logger
basename = "daemon_boilerplate"
log_file = "/var/log/{0}.log".format(basename)
log_options = LogOptions(basename, path=log_file)
logger = get_logger(log_options)

if __name__ == "__main__":
    # Returns argparse.Namespace; to pass into function, use **vars(self.args)
    def parse_arguments():
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("action", choices=["restart", "stop", "start"])
        parser.add_argument("--debug", action="store_true")
        return parser.parse_args()
    args = parse_arguments()

    # Configure the logger
    log_level = 20                  # logging.INFO
    if args.debug: log_level = 10   # logging.DEBUG
    logger.setLevel(log_level)
    logger.debug("(__main__): args: {0}".format(args))
    logger.debug("(__main__): ------------------------------------------------")

    # Initialize the daemon
    class TestDaemon(DaemonContext):
        # DaemonContext remains alive so long as 'while' loop continues
        def run(self):
            logger.debug("(TestDaemon:run): Init")
            # Main heartbeat for business logic
            self.counter = 0
            while True:
                self.test_tasks()
                time.sleep(3)

        # Test writing to files
        def test_tasks(self):
            # logger.debug("(TestDaemon:test_tasks): Init")
            testFile = "/tmp/ewertz"
            self.counter += 1
            message = "Daemon counter: {0}".format(self.counter)
            sh.file_write(testFile, message, True)
            return

    daemon = TestDaemon(basename, log_file)

    # --- Business Logic ---
    if args.action in ["stop", "restart"]:
        daemon.close()
    if args.action in ["start", "restart"]:
        daemon.open()
    # Assume all is well if here
    sh.process_exit()


    # --- Usage Example ---
    # sudo python /root/.local/lib/python2.7/site-packages/daemon_boilerplate.py
    # sudo python /root/.local/lib/python2.7/site-packages/daemon_boilerplate.py --debug && sudo less +F /var/log/daemon_boilerplate.log
    # ps -eaf | grep -i python

    # sudo ls -la /var/run/daemon_boilerplate.pid
    # sudo ls -la /var/lock/daemon_boilerplate
    # sudo ls -la /var/log/daemon_boilerplate.log
    # sudo ls -la /tmp/ewertz
