#!/usr/bin/env python
"""Common logic for Python Azure DevOps interactions"""

# --- Global Azure Methods ---
# user:                         user_get, user_list, user_logout, user_login, user_set
# devops:                       devops_config
# devops project:               devops_project_list, devops_project_create

# TODO:
# artifacts:                    artifact_set, artifact_get
# boards:                       board_set, board_get
# pipelines:                    pipeline_set, pipeline_get
# repos:                        repo_set, repo_get

import argparse
from typing import List, Tuple

import logging_boilerplate as log
import shell_boilerplate as sh

# ------------------------ Global Methods ------------------------

# --- DevOps User Commands ---
# https://docs.microsoft.com/en-us/cli/azure/ext/azure-devops/devops (login)
# https://docs.microsoft.com/en-us/cli/azure/ext/azure-devops/devops/user


def user_get(pat_data: str, user: str) -> bool:
    """Method that fetches Azure DevOps user profile"""
    command: List[str] = ["az", "devops", "user", "show", f"--user={user}"]
    environment_vars = {'AZURE_DEVOPS_EXT_PAT': pat_data}
    sh.print_command(command)
    # process = sh.run_subprocess(command)
    process = sh.run_subprocess(command, env=environment_vars)
    # sh.log_subprocess(LOG, process, debug=ARGS.debug)
    return process.returncode == 0


def user_logout() -> bool:
    """Method that signs out Azure DevOps user profile"""
    command: List[str] = ["az", "devops", "logout"]
    sh.print_command(command)
    process = sh.run_subprocess(command)
    sh.log_subprocess(LOG, process, debug=ARGS.debug)
    return process.returncode == 0


# # Login with credential (PAT)
# def user_login(pat_path: str = "ado.pat", pat_data: str = ""):
#     if not sh.path_exists(pat_path, "f"):
#         return False
#     command = ["cat", pat_path, "|", "az", "devops", "login"]
#     # Print password-safe version of command
#     # sh.print_command("az devops login")
#     sh.print_command(command)
#     environment_vars = {
#         'AZURE_DEVOPS_EXT_PAT': pat_data
#     }
#     process = sh.run_subprocess(command, shell=True)
#     sh.log_subprocess(LOG, process, debug=ARGS.debug)
#     results = bool(process.returncode == 0)
#     LOG.debug(f"results: {results}")
#     return results


# Login with credential (PAT)
def user_login(pat_data: str) -> bool:
    """Method that signs into Azure DevOps user profile"""
    command: List[str] = ["az", "devops", "login"]
    environment_vars = {'AZURE_DEVOPS_EXT_PAT': pat_data}
    sh.print_command(command)
    process = sh.run_subprocess(command, env=environment_vars)
    # sh.log_subprocess(LOG, process, debug=ARGS.debug)
    return process.returncode == 0


# def user_save(path: str, service_principal: ServicePrincipal):
#     LOG.info("storing service principal credentials...")
#     sh.json_save(path, service_principal.__dict__)
#     LOG.info("successfully saved service principal credentials!")


def user_save(path: str, content: str):
    """Method that saves Azure DevOps user profile to a file"""
    # Handle previous credentials if found
    if sh.path_exists(path, "f"):
        backup_path = sh.backup_file(path)
    LOG.debug("storing user PAT/credentials...")
    sh.write_file(path, content)
    LOG.debug("successfully saved user PAT/credentials!")


# --- DevOps Project Commands ---
# https://docs.microsoft.com/en-us/cli/azure/ext/azure-devops/devops/project

def devops_project_list() -> Tuple[bool, bool]:
    """Method that lists Azure DevOps projects"""
    command: List[str] = ["az", "devops", "project", "--list"]
    sh.print_command(command)
    process = sh.run_subprocess(command)
    sh.log_subprocess(LOG, process, debug=ARGS.debug)
    failed = (process.returncode != 0)
    changed = (not failed and "is not authorized to access this resource" not in process.stderr)
    return (not failed, changed)


# ------------------------ Main Program ------------------------
# Initialize the logger
BASENAME = "azure_devops_boilerplate"
ARGS: argparse.Namespace = argparse.Namespace()  # for external modules
LOG: log.Logger = log.get_logger(BASENAME)

if __name__ == "__main__":
    # Returns argparse.Namespace; to pass into function, use **vars(self.ARGS)
    def parse_arguments():
        """Method that parses arguments provided"""
        parser = argparse.ArgumentParser()
        parser.add_argument("--debug", action="store_true")
        parser.add_argument("--log-path", default="")
        return parser.parse_args()
    ARGS = parse_arguments()

    #  Configure the main logger
    LOG_HANDLERS: List[log.LogHandlerOptions] = log.default_handlers(ARGS.debug, ARGS.log_path)
    log.set_handlers(LOG, LOG_HANDLERS)
    if ARGS.debug:
        # Configure the shell_boilerplate logger
        _sh_log = log.get_logger("shell_boilerplate")
        log.set_handlers(_sh_log, LOG_HANDLERS)
        sh.ARGS.debug = ARGS.debug

    LOG.debug(f"ARGS: {ARGS}")
    LOG.debug("------------------------------------------------")

    # --- Usage Example ---
    # python ~/.local/lib/python2.7/site-packages/azure_devops_boilerplate.py --debug
    # python ~/.local/lib/python3.6/site-packages/azure_devops_boilerplate.py --debug
