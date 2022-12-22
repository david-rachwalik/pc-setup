#!/usr/bin/env python
"""Command to perform common Git strategies"""

# Basename: mygit
# Description: A service to control common Git business logic
# Version: 1.2.0
# VersionDate: 11 Sep 2020

#       *** Actions ***
# push:                 Either pull or create a bare repository; then push
# pull:                 Auto-resolve using 'ours' merge strategy; favors existing changes
# reset:                Disregard existing working directory changes; match files to remote
# status:               Determines whether the work-tree is clean (True) or dirty (False)
# delete:               Removes the specified branch in locl and remote repositories
#       *** Options ***
# --debug:              Enable to display log messages for development
# --force:              Enable to disregard the initialize repository prompt
# --branch:             Arbitrary name of branch to push/pull; default is 'master'
# --remote-alias:       Alias used for bare repo; default is 'origin'
# --remote-path:        Remote, bare repository path (origin)
# --local-path:         Specify where to create work repo; default is current directory
# --gitignore-path:     Location of .gitignore file to use

# from typing import Dict, List, Optional, Tuple
from typing import List

import git_boilerplate as bp_git
import logging_boilerplate as log
import shell_boilerplate as sh

try:
    # Python 2 has both 'str' (bytes) and 'unicode' text
    basestring = basestring
    unicode = unicode
except NameError:
    # Python 3 names the unicode data type 'str'
    basestring = str
    unicode = str

# ------------------------ Primary classes/functions ------------------------

# Provide 'remote_path' for bare repo; 'no_create' only applies to bare


class Repository(object):
    def __init__(self, path, remote_path="", no_create=False, force=False):
        # _log.debug("(Repository:__init__): Init")
        self.path = str(path)
        self.remote_path = str(remote_path) if remote_path else ""
        self.force = bool(force)
        self.is_bare = not bool(self.remote_path)
        self.repo_descriptor = "remote, bare" if self.is_bare else "local, work"

        self.exists = bp_git.repo_exists(self.path, self.is_bare)
        if self.exists:
            _log.debug(f"(Repository:__init__): Successfully found {0} repository".format(
                self.repo_descriptor))
        else:
            _log.debug(f"(Repository:__init__): Unable to locate {0} repository".format(
                self.repo_descriptor))
            if not no_create:
                self.create()
            else:
                _log.error(f"(Repository:__init__): Cannot proceed; missing {0} repository".format(
                    self.repo_descriptor))
                sh.process_fail()

    def create(self):
        # _log.debug("(Repository:create): Init")
        display_path = self.path if (
            self.is_bare) else f"{0}/.git".format(self.path)
        if not self.force:
            response = input(
                f"Repository not found ({0}), initialize?  (y or yes): ".format(display_path))
            if response.lower() not in ["y", "yes"]:
                _log.info("Exiting without creating repository")
                sh.process_fail()
        else:
            _log.info(
                f"Repository not found ({0}), initializing...".format(display_path))

        # Initialize the repository
        (self.exists, changed) = bp_git.repo_create(self.path, self.is_bare)
        if self.exists:
            _log.info("Repository successfully created!")
        else:
            _log.error(f"(Repository:create): Unable to create {0} repository".format(
                self.repo_descriptor))
            sh.process_fail()


class GitController(object):
    def __init__(self):
        # _log.debug("(GitController): Init")
        _log.debug(f"ARGS: {0}".format(ARGS))
        _log.info(f"Git '{0}' action detected".format(ARGS.action))
        _log.debug(
            "--------------------------------------------------------")

        # ------------------------ Bare Repo (remote repository) ------------------------

        # Ensure bare repo exists
        if (ARGS.action in ["status", "reset"]):
            _log.debug(
                f"(GitController): skip bare repository check for '{0}' action".format(ARGS.action))
        else:
            # fail when not 'push' action and repo is missing
            no_create = (ARGS.action != "push")
            self.bare_repository = Repository(
                ARGS.remote_path, no_create=no_create, force=True)
            _log.debug(f"(GitController): bare_repository exists: {0}".format(
                self.bare_repository.exists))

        # ------------------------ Work Repo (local repository) ------------------------

        # Ensure work repo exists
        # fail when not 'push' action and repo is missing
        no_create = (ARGS.action != "push")
        self.work_repository = Repository(
            ARGS.local_path, ARGS.remote_path, no_create=no_create, force=True)
        _log.debug(f"(GitController): work_repository exists: {0}".format(
            self.work_repository.exists))

        # Set work repo's remote path to bare repo
        remote_result = bp_git.work_remote(
            ARGS.local_path, ARGS.remote_path, ARGS.remote_alias)
        if not remote_result:
            _log.error(
                "(GitController): Error occurred updating remote path")
            sh.process_fail()

        # Fetch the latest meta data; increases '.git' directory size
        if ARGS.action in ["push", "pull"]:
            bp_git.work_fetch(ARGS.local_path)

        # Update '.gitignore' based on hash check
        if ARGS.action in ["push", "pull"] and len(ARGS.gitignore_path) > 0:
            file_src = ARGS.gitignore_path
            file_dest = sh.path_join(ARGS.local_path, ".gitignore")
            if sh.path_exists(file_dest, "f"):
                hash_result = sh.file_match(file_src, file_dest)
                if not hash_result:
                    _log.debug(
                        "(GitController): '.gitignore' hashes don't match, updating...")
                    update_result = sh.file_copy(file_src, file_dest)
                    if update_result:
                        _log.debug(
                            "(GitController): '.gitignore' was successfully updated!")
                    else:
                        _log.debug(
                            "(GitController): '.gitignore' failed to be updated")
                        sh.process_fail()
                else:
                    _log.debug(
                        "(GitController): '.gitignore' is already up-to-date")
            else:
                _log.debug(
                    "(GitController): '.gitignore' is missing, adding...")
                add_result = sh.file_copy(file_src, file_dest)
                if add_result:
                    _log.debug(
                        "(GitController): '.gitignore' was successfully added!")
                else:
                    _log.debug(
                        "(GitController): '.gitignore' failed to be added")
                    sh.process_fail()

        # ------------------------ Validation Checks ------------------------

        _log.debug("---------------- Validation Checks ----------------")

        # Check work-tree status
        work_tree_is_clean = bp_git.work_status(ARGS.local_path)
        _log.debug(
            f"(GitController): work-tree is clean: {0}".format(work_tree_is_clean))
        # Gather cache of branch names (fewer queries to refs)
        local_branches = bp_git.branch_list(ARGS.local_path)
        remote_branches = bp_git.branch_list(
            ARGS.local_path, ARGS.remote_alias)
        # Check for branches in 'refs/heads' and 'refs/remotes'
        master_local_branch_exists = bp_git.branch_exists(
            ARGS.local_path, master_branch, branches=local_branches)
        master_remote_branch_exists = bp_git.branch_exists(
            ARGS.local_path, master_branch, ARGS.remote_alias, branches=remote_branches)
        _log.debug(f"(GitController): master_local_branch_exists: {0}".format(
            master_local_branch_exists))
        _log.debug(f"(GitController): master_remote_branch_exists: {0}".format(
            master_remote_branch_exists))
        stash_local_branch_exists = bp_git.branch_exists(
            ARGS.local_path, stash_branch, branches=local_branches)
        _log.debug(f"(GitController): stash_local_branch_exists: {0}".format(
            stash_local_branch_exists))
        version_local_branch_exists = bp_git.branch_exists(
            ARGS.local_path, ARGS.branch, branches=local_branches)
        version_remote_branch_exists = bp_git.branch_exists(
            ARGS.local_path, ARGS.branch, ARGS.remote_alias, branches=remote_branches)
        _log.debug(f"(GitController): version_local_branch_exists: {0}".format(
            version_local_branch_exists))
        _log.debug(f"(GitController): version_remote_branch_exists: {0}".format(
            version_remote_branch_exists))

        # Fail early when attempting to pull/delete a dirty work-tree
        if ARGS.action in ["pull", "delete"] and not work_tree_is_clean:
            _log.error(
                f"(GitController): Unable to perform '{0}' action with dirty work-tree".format(ARGS.action))
            sh.process_fail()

        # Fail early when attempting to delete 'master' branch; assumed to always exist after initial commit
        if ARGS.action == "delete" and ARGS.branch == master_branch:
            _log.error(
                f"(GitController): Unable to delete the '{0}' branch".format(master_branch))
            sh.process_fail()

        # Fail early when attempting to pull 'master' or 'version' branch that's missing from bare repo
        if ARGS.action == "pull":
            if not master_remote_branch_exists:
                _log.error(f"(GitController): Unable to perform '{0}' action; '{1}/{2}' branch not found".format(
                    ARGS.action, ARGS.remote_alias, master_branch))
                sh.process_fail()
            if not version_remote_branch_exists:
                _log.error(f"(GitController): Unable to perform '{0}' action; '{1}/{2}' branch not found".format(
                    ARGS.action, ARGS.remote_alias, ARGS.branch))
                sh.process_fail()

        # ------------------------ 'master' branch ------------------------

        _log.debug("---------------- Master Branch Steps ----------------")

        # 'master' branch should always exist; regardless whether it's the focus of this run
        if ARGS.action in ["push", "pull"] and not master_local_branch_exists:
            if master_remote_branch_exists:
                # Switch to bare repo 'master' branch before any commits
                bp_git.branch_switch(
                    ARGS.local_path, master_branch, ARGS.remote_alias)
                _log.debug(
                    f"(GitController): checked out '{0}/{1}' branch".format(ARGS.remote_alias, master_branch))
                master_local_branch_exists = bp_git.branch_create(
                    ARGS.local_path, master_branch)
                _log.debug(f"(GitController): created local '{1}' branch from remote '{0}/{1}' branch".format(
                    ARGS.remote_alias, master_branch))
            else:
                # Push initial 'master' branch to remote when not already there
                _log.warning(
                    f"(GitController): '{0}' branch is missing, creating initial commit...".format(master_branch))
                (commit_succeeded, commit_changed) = bp_git.work_commit(
                    ARGS.local_path, initial=True)
                _log.info(
                    f"Intial commit for '{0}' branch successfully created!".format(master_branch))
                # 'master' branch automatically active after initial commit; explicit checkout unnecessary

                (push_succeeded, push_changed) = bp_git.work_push(
                    ARGS.local_path, master_branch, ARGS.remote_alias)
                _log.debug(f"(GitController): initial push to '{0}/{1}' has succeeded: {2}".format(
                    ARGS.remote_alias, master_branch, push_succeeded))
                # No need to refresh metadata again; push will update references

        # ------------------------ 'my-stash' branch ------------------------

        _log.debug("---------------- Stash Branch Steps ----------------")

        # When work-tree is dirty, commit the changes to 'my-stash' branch
        if ARGS.action == "push" and version_remote_branch_exists and not work_tree_is_clean:
            _log.debug(
                "(GitController): preparing to stash work-tree changes...")

            # Create 'my-stash' branch from local 'master' branch
            bp_git.branch_switch(ARGS.local_path, master_branch)
            _log.debug(
                f"(GitController): checked out '{0}' branch".format(master_branch))

            # Check if stash branch already exists, delete if so
            if stash_local_branch_exists:
                _log.debug(f"(GitController): previous '{0}' branch was detected, removing...".format(
                    work_tree_is_clean))
                bp_git.branch_delete(ARGS.local_path, stash_branch)
                _log.debug(f"(GitController): '{0}' branch was deleted".format(
                    work_tree_is_clean))

            # Create and checkout 'my-stash' branch to stage and commit those dirty files
            stash_local_branch_exists = bp_git.branch_create(
                ARGS.local_path, stash_branch)
            bp_git.branch_switch(ARGS.local_path, stash_branch)
            _log.debug(
                f"(GitController): created and checked out '{0}' branch".format(stash_branch))
            (commit_succeeded, commit_changed) = bp_git.work_commit(ARGS.local_path)
            _log.debug(f"(GitController): commit for '{0}' branch succeeded: {1}".format(
                stash_branch, commit_succeeded))

            # Verify work-tree status (should always be clean after commit)
            work_tree_is_clean = bp_git.work_status(ARGS.local_path)
            _log.debug(
                f"(GitController): work-tree is clean: {0}".format(work_tree_is_clean))

        # ------------------------ 'version' branch ------------------------

        _log.debug("---------------- Version Branch Steps ----------------")
        # -------- Avoid checkout of branch until work-tree is clean --------

        # Create local 'version' branch if missing
        if ARGS.action in ["push", "pull"]:
            version_branch_just_created = False
            if not version_local_branch_exists:
                if version_remote_branch_exists:
                    # Create local 'version' branch from bare repo
                    bp_git.branch_switch(
                        ARGS.local_path, ARGS.branch, ARGS.remote_alias)
                    _log.debug(
                        f"(GitController): checked out '{0}/{1}' branch".format(ARGS.remote_alias, ARGS.branch))
                    version_local_branch_exists = bp_git.branch_create(
                        ARGS.local_path, ARGS.branch)
                    _log.debug(f"(GitController): created local '{1}' branch from remote '{0}/{1}' branch".format(
                        ARGS.remote_alias, ARGS.branch))
                else:
                    # Create local 'version' branch from 'master' branch
                    bp_git.branch_switch(ARGS.local_path, master_branch)
                    _log.debug(
                        f"(GitController): checked out '{0}' branch".format(master_branch))
                    version_local_branch_exists = bp_git.branch_create(
                        ARGS.local_path, ARGS.branch)
                    _log.debug(f"(GitController): created local '{1}' branch from '{0}' branch".format(
                        master_branch, ARGS.branch))
                version_branch_just_created = True

                # Verify successfully created 'version' branch
                if not version_local_branch_exists:
                    _log.error(
                        f"(GitController): local '{0}' branch still appears to be missing; failed to create".format(ARGS.branch))
                    sh.process_fail()

                # Checkout local 'version' branch
                bp_git.branch_switch(ARGS.local_path, ARGS.branch)

            # Commit changes to local 'version' branch; not using 'my-stash' branch because remote 'version' branch is missing
            if ARGS.action == "push":
                # When work-tree is dirty, commit changes to 'version' branch
                if not work_tree_is_clean and not version_remote_branch_exists:
                    (commit_succeeded, commit_changed) = bp_git.work_commit(
                        ARGS.local_path)
                    _log.debug(f"(GitController): commit for '{0}' branch succeeded: {1}".format(
                        ARGS.branch, commit_succeeded))
                    # Verify work-tree status (should always be clean after commit)
                    work_tree_is_clean = bp_git.work_status(ARGS.local_path)
                    _log.debug(f"(GitController): work_tree_is_clean: {0}".format(
                        work_tree_is_clean))

            # Merge remote 'version' branch into local when both exist and local wasn't just created
            if ARGS.action in ["push", "pull"]:
                if version_remote_branch_exists and not version_branch_just_created:
                    # Merge 'version' branch from bare repo into work repo
                    _log.debug(f"(GitController): merge '{0}/{1}' branch into local '{0}' branch".format(
                        ARGS.remote_alias, ARGS.branch))
                    (succeeded, changed) = bp_git.work_merge(
                        ARGS.local_path, ARGS.branch, ARGS.remote_alias)
                    _log.debug(f"(GitController): '{0}/{1}' branch merge succeeded: {2}".format(
                        ARGS.remote_alias, ARGS.branch, succeeded))

            # Rebase local 'my-stash' branch onto local 'version' branch
            if ARGS.action == "push" and stash_local_branch_exists:
                bp_git.branch_switch(ARGS.local_path, stash_branch)
                _log.debug(
                    f"(GitController): checked out '{0}' branch".format(stash_branch))
                _log.debug(f"(GitController): rebasing '{0}' branch onto local '{1}' branch...".format(
                    stash_branch, ARGS.branch))
                (succeeded, changed) = bp_git.work_rebase(
                    ARGS.local_path, ARGS.branch)
                _log.debug(f"(GitController): '{0}' branch rebase succeeded: {1}".format(
                    stash_branch, succeeded))
                # Checkout local 'version' branch
                bp_git.branch_switch(ARGS.local_path, ARGS.branch)
                # Delete 'my-stash' branch
                bp_git.branch_delete(ARGS.local_path, stash_branch)

        # TODO: other action steps
        if ARGS.action == "reset":
            # Hard reset will also clear any pending (unpushed) commits
            _log.info("(GitController): ::mock:: reset action")
            # bp_git.work_reset(ARGS.local_path, ARGS.branch, ARGS.remote_alias)

        elif ARGS.action == "delete":
            # Deleting both local and remote branches, no pull steps needed
            _log.debug(
                f"(GitController): deleting '{0}' branch...".format(ARGS.branch))
            # Checkout local 'master' branch
            bp_git.branch_switch(ARGS.local_path, master_branch)
            # Delete 'version' branch
            bp_git.branch_delete(ARGS.local_path, ARGS.branch)
            bp_git.branch_delete(ARGS.remote_path, ARGS.branch)
            _log.debug(
                f"(GitController): '{0}' branch deleted".format(ARGS.branch))

        elif ARGS.action == "status":
            # Verify work-tree status and display status statement
            work_tree_is_clean = bp_git.work_status(ARGS.local_path)
            _log.info(f"work_tree_is_clean: {0}".format(work_tree_is_clean))

        # Push to bare repo
        if ARGS.action == "push":
            # Push 'version' branch to bare repo
            _log.debug(f"(GitController): pushing '{0}' branch to {1}".format(
                ARGS.branch, ARGS.remote_alias))
            (push_succeeded, push_changed) = bp_git.work_push(
                ARGS.local_path, ARGS.branch, ARGS.remote_alias)
            _log.debug(f"(GitController): '{0}/{1}' branch push has succeeded: {2}".format(
                ARGS.remote_alias, ARGS.branch, push_succeeded))
            # No need to refresh metadata again; the push will update references


# ------------------------ Main program ------------------------
master_branch = "master"
stash_branch = "my-stash"

# Initialize the logger
BASENAME = "mygit"
# log_file = "/var/log/{0}.log".format(basename)
# log_options = LogOptions(BASENAME)
# logger = log.get_logger(log_options)
# ARGS = log.LogArgs()  # for external modules
_log: log.Logger = log.get_logger(BASENAME)

if __name__ == "__main__":
    def parse_arguments():
        """Method that parses arguments provided"""
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("action", choices=[
                            "push", "pull", "reset", "status", "delete"])
        parser.add_argument("--debug", action="store_true")
        parser.add_argument("--force", "-f", action="store_true")
        parser.add_argument("--branch", "-b", default=master_branch)
        parser.add_argument("--remote-alias", default="origin")
        parser.add_argument("--remote-path", default="~/my_origin_repo.git")
        parser.add_argument("--local-path", default=sh.path_current())
        parser.add_argument("--gitignore-path", default="")
        return parser.parse_args()
    ARGS = parse_arguments()

    #  Configure the main logger
    log_handlers: List[log.LogHandlerOptions] = log.default_handlers(
        ARGS.debug, ARGS.log_path)
    log.set_handlers(_log, log_handlers)

    _log.debug(f"ARGS: {0}".format(ARGS))
    _log.debug("------------------------------------------------")

    # Configure the logger
    log_level = 20                  # logging.INFO
    if ARGS.debug:
        log_level = 10   # logging.DEBUG
    _log.setLevel(log_level)

    # Configure the shell_boilerplate logger
    if ARGS.debug:
        sh_logger = log.get_logger("shell_boilerplate")
        sh_logger.setLevel(log_level)

    # Configure the git_boilerplate logger
    if ARGS.debug:
        git_logger = log.get_logger("git_boilerplate")
        git_logger.setLevel(log_level)

    controller = GitController()

    # If we get to this point, assume all went well
    _log.debug("--------------------------------------------------------")
    _log.debug("--- end point reached :3 ---")
    sh.process_exit()

    # :: Usage Example ::
    # mygit push --branch="Zoolander"
    # mygit push --debug --force --branch="Zoolander" --gitignore-path="~/.gitignore"
