#!/usr/bin/env python

# Basename: azure_boilerplate
# Description: Common business logic for Azure resources
# Version: 0.0.1
# VersionDate: 12 Sep 2020

# --- Global Git Commands ---
# authentication:               subscription_login, service_principal_create
# resource group:               rg_create, rg_delete


# Repository (bare/work):       repo_exists, repo_create
# Working Directory:            work_remote, work_status, work_commit, work_push
# - meta reference:             ref_head, ref_heads, ref_remotes, ref_tags
# - branch:                     branch_validate, branch_exists, branch_create, branch_switch, branch_delete
# - pull methods:               work_fetch, work_merge, work_rebase, work_reset

from logging_boilerplate import *
import shell_boilerplate as sh

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


# ------------------------ Main Program ------------------------

# Initialize the logger
basename = "azure_boilerplate"
log_options = LogOptions(basename)
logger = get_logger(log_options)

if __name__ == "__main__":
    def parse_arguments():
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--debug", action="store_true")
        return parser.parse_args()
    args = parse_arguments()

    # Configure the logger
    log_level = 20                  # logging.INFO
    if args.debug: log_level = 10   # logging.DEBUG
    logger.setLevel(log_level)
    logger.debug("(__main__): args: {0}".format(args))
    logger.debug("(__main__): ------------------------------------------------")


    # --- Usage Example ---
    # sudo python /root/.local/lib/python2.7/site-packages/azure_boilerplate.py
    # sudo python /root/.local/lib/python2.7/site-packages/azure_boilerplate.py --debug
