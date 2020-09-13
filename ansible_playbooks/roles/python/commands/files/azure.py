#!/usr/bin/env python

# Basename: azure
# Description: A service to control common Azure business logic
# Version: 0.0.2
# VersionDate: 12 Sep 2020

#         *** Actions ***
# login:            Ensure credential file exists or prompts manual login to create
# show:                Print output for a resource, key vault secret, etc.
# deploy:            Deploy an application to Azure (webapp, api, nuget package)
# status:            View running state of deployed application
#         *** Options ***
# --debug:             Enable to display log messages for development
# --quiet:            Enable to reduce verbosity and disregard the manual login prompt

from logging_boilerplate import *
import shell_boilerplate as sh
import azure_boilerplate as az

try:
    # Python 2 has both 'str' (bytes) and 'unicode' text
    basestring = basestring
    unicode = unicode
except NameError:
    # Python 3 names the unicode data type 'str'
    basestring = str
    unicode = str

# ------------------------ Global Azure Commands ------------------------

# --- Subscription Commands ---

def login(path, version="master", remote_alias=""):
    # logger.debug("(work_reset): Init")
    # Reset branch to latest (auto-resolve)
    remote_branch = "{0}/{1}".format(remote_alias, version)
    use_branch = remote_branch if remote_alias else version
    command = ["git", "reset", "--hard", use_branch]
    logger.debug("(work_reset): command => {0}".format(str.join(" ", command)))
    (rc, stdout, stderr) = sh.subprocess_await(command, path)
    # logger.debug("(work_reset): rc: {0}".format(rc))
    # if len(stdout) > 0: logger.info(str(stdout))
    # if len(stderr) > 0: logger.error(str(stderr))
    return (rc == 0)


# ------------------------ Main program ------------------------

# Initialize the logger
basename = "azure"
log_file = "/var/log/{0}.log".format(basename)
log_options = LogOptions(basename)
logger = get_logger(log_options)

if __name__ == "__main__":
    def parse_arguments():
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("action", choices=["login", "show", "deploy", "status"])
        parser.add_argument("--debug", action="store_true")
        return parser.parse_args()
    args = parse_arguments()

    # Configure the logger
    log_level = 20                  # logging.INFO
    if args.debug: log_level = 10   # logging.DEBUG
    logger.setLevel(log_level)

    # If we get to this point, assume all went well
    logger.debug("--------------------------------------------------------")
    logger.debug("--- end point reached :3 ---")
    sh.process_exit()

    # :: Usage Example ::
    # setup --tags "py" --skip-tags "windows"
    # azure --debug
