#!/usr/bin/env python
"""Common logic for Python Azure DevOps interactions"""

# Basename: azure_devops_boilerplate
# Description: Common business logic for Azure resources
# Version: 1.0.0
# VersionDate: 19 Oct 2021

# --- Global Azure Methods ---
# user:                         user_get, user_list, user_logout, user_login, user_set
# devops:                       devops_config
# devops project:               devops_project_list, devops_project_create

# TODO:
# artifacts:                    artifact_set, artifact_get
# boards:                       board_set, board_get
# pipelines:                    pipeline_set, pipeline_get
# repos:                        repo_set, repo_get

from typing import List, Tuple

import logging_boilerplate as log
import shell_boilerplate as sh

# ------------------------ Global Methods ------------------------

# --- DevOps User Commands ---
# https://docs.microsoft.com/en-us/cli/azure/ext/azure-devops/devops (login)
# https://docs.microsoft.com/en-us/cli/azure/ext/azure-devops/devops/user


def user_get(pat_data: str, user: str) -> bool:
    """Method that fetches Azure DevOps user profile"""
    if not (pat_data and isinstance(pat_data, str)):
        TypeError("'pat_data' parameter expected as string")
    if not (user and isinstance(user, str)):
        TypeError("'user' parameter expected as string")
    command: List[str] = ["az", "devops", "user", "show", f"--user={0}".format(user)]
    environment_vars = {'AZURE_DEVOPS_EXT_PAT': pat_data}
    sh.print_command(command)
    # (stdout, stderr, rc) = sh.subprocess_run(command)
    (stdout, stderr, rc) = sh.subprocess_run(command, env=environment_vars)
    # sh.subprocess_log(_log, stdout, stderr, rc, debug=ARGS.debug)
    return bool(rc == 0)


def user_logout() -> bool:
    """Method that signs out Azure DevOps user profile"""
    command: List[str] = ["az", "devops", "logout"]
    sh.print_command(command)
    (stdout, stderr, rc) = sh.subprocess_run(command)
    sh.subprocess_log(_log, stdout, stderr, rc, debug=ARGS.debug)
    return bool(rc == 0)


# # Login with credential (PAT)
# def user_login(pat_path="ado.pat", pat_data=""):
#     if not (pat_path and isinstance(pat_path, str)): TypeError("'pat_path' parameter expected as string")
#     if not (pat_data and isinstance(pat_data, str)): TypeError("'pat_data' parameter expected as string")
#     if not sh.path_exists(pat_path, "f"): return False
#     command = ["cat", pat_path, "|", "az", "devops", "login"]
#     # Print password-safe version of command
#     # sh.print_command("az devops login")
#     sh.print_command(command)
#     environment_vars = {
#         'AZURE_DEVOPS_EXT_PAT': pat_data
#     }
#     (stdout, stderr, rc) = sh.subprocess_run(command, shell=True)
#     sh.subprocess_log(_log, stdout, stderr, rc, debug=ARGS.debug)
#     results = bool(rc == 0)
#     _log.debug("results: {0}".format(results))
#     return results


# Login with credential (PAT)
def user_login(pat_data: str) -> bool:
    """Method that signs into Azure DevOps user profile"""
    if not (pat_data and isinstance(pat_data, str)):
        TypeError("'pat_data' parameter expected as string")
    command: List[str] = ["az", "devops", "login"]
    environment_vars = {'AZURE_DEVOPS_EXT_PAT': pat_data}
    sh.print_command(command)
    (stdout, stderr, rc) = sh.subprocess_run(command, env=environment_vars)
    # sh.subprocess_log(_log, stdout, stderr, rc, debug=ARGS.debug)
    return bool(rc == 0)


# def user_save(path, service_principal):
#     if not (path and isinstance(path, str)): TypeError("'path' parameter expected as string")
#     if not isinstance(service_principal, ServicePrincipal): TypeError("'service_principal' parameter expected as ServicePrincipal")
#     _log.info("storing service principal credentials...")
#     sh.json_save(path, service_principal.__dict__)
#     _log.info("successfully saved service principal credentials!")


def user_save(path: str, content: str):
    """Method that saves Azure DevOps user profile to a file"""
    if not (path and isinstance(path, str)):
        TypeError("'path' parameter expected as string")
    if not (content and isinstance(content, str)):
        TypeError("'content' parameter expected as string")
    # Handle previous credentials if found
    if sh.path_exists(path, "f"):
        backup_path = sh.file_backup(path)
    _log.debug("storing user PAT/credentials...")
    sh.file_write(path, content)
    _log.debug("successfully saved user PAT/credentials!")


# --- DevOps Project Commands ---
# https://docs.microsoft.com/en-us/cli/azure/ext/azure-devops/devops/project

def devops_project_list() -> Tuple[bool, bool]:
    """Method that lists Azure DevOps projects"""
    command: List[str] = ["az", "devops", "project", "--list"]
    sh.print_command(command)
    (stdout, stderr, rc) = sh.subprocess_run(command)
    sh.subprocess_log(_log, stdout, stderr, rc, debug=ARGS.debug)
    failed = (rc != 0)
    changed = (not failed and "is not authorized to access this resource" not in stderr)
    return (not failed, changed)


# ------------------------ Main Program ------------------------
# Initialize the logger
BASENAME: str = "azure_devops_boilerplate"
ARGS = log.LogArgs()  # for external modules
_log: log._logger_type = log.get_logger(BASENAME)

if __name__ == "__main__":
    # Returns argparse.Namespace; to pass into function, use **vars(self.ARGS)
    def parse_arguments():
        """Method that parses arguments provided"""
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--debug", action="store_true")
        parser.add_argument("--log-path", default="")
        return parser.parse_args()
    ARGS = parse_arguments()

    #  Configure the main logger
    log_handlers: List[log.LogHandlerOptions] = log.default_handlers(ARGS.debug, ARGS.log_path)
    log.set_handlers(_log, log_handlers)
    if ARGS.debug:
        # Configure the shell_boilerplate logger
        _sh_log = log.get_logger("shell_boilerplate")
        log.set_handlers(_sh_log, log_handlers)
        sh.ARGS.debug = ARGS.debug

    _log.debug(f"ARGS: {0}".format(ARGS))
    _log.debug("------------------------------------------------")

    # --- Usage Example ---
    # python ~/.local/lib/python2.7/site-packages/azure_devops_boilerplate.py --debug
    # python ~/.local/lib/python3.6/site-packages/azure_devops_boilerplate.py --debug
