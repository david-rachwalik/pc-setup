#!/usr/bin/env python

# Basename: git_boilerplate
# Description: Common business logic for Git (v1.8.x)
# Version: 1.2.1
# VersionDate: 26 Aug 2020

# --- Global Git Commands ---
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

# ------------------------ Global Git Commands ------------------------

# --- Repository (bare/work) Commands ---

def repo_exists(path, bare=False):
    # logger.debug("(repo_exists): Init")
    result = False
    if bare:
        if sh.path_exists(path, "d"):
            command = ["git", "rev-parse", "--is-bare-repository"]
            logger.debug("(repo_exists): command => {0}".format(str.join(" ", command)))
            (rc, stdout, stderr) = sh.subprocess_await(command, path)
            # logger.debug("(repo_exists): rc: {0}".format(rc))
            # logger.debug("(repo_exists): stdout: {0}".format(stdout))
            result = (rc == 0 and stdout == "true")
    else:
        result = sh.path_exists("{0}/.git".format(path), "d")
    # logger.debug("(repo_exists): result: {0}".format(result))
    return result


# Initialize the repository
def repo_create(path, bare=False):
    # logger.debug("(repo_create): Init")
    command = ["git", "init"]
    if bare:
        sh.directory_create(path) # Directory must exist prior
        command.append("--bare")
    logger.debug("(repo_create): command => {0}".format(str.join(" ", command)))
    (rc, stdout, stderr) = sh.subprocess_await(command, path)
    # logger.debug("(repo_create): rc: {0}".format(rc))
    # logger.debug("(repo_create): stdout: {0}".format(stdout))
    # logger.debug("(repo_create): stderr: {0}".format(stderr))
    failed = (rc != 0 and "Reinitialized existing Git repository" not in stdout)
    changed = (not failed and "skipped, since" not in stdout)
    return (not failed, changed)


# --- Repository (work) Commands ---

# Ensure remote path links to bare repository
def work_remote(path, remote_path, remote_alias="origin"):
    logger.debug("(work_remote): Init")
    succeeded = False
    # Check local repository for remote alias
    command = ["git", "config", "--get", "remote.{0}.url".format(remote_alias)]
    (rc, stdout, stderr) = sh.subprocess_await(command, path)
    if not stdout:
        # Repository is missing remote path, adding...
        logger.warning("Remote ({0}) for local repository is missing, adding...".format(remote_alias))
        command = ["git", "remote", "add", remote_alias, remote_path]

        logger.debug("(work_remote): command => {0}".format(str.join(" ", command)))
        (rc, stdout, stderr) = sh.subprocess_await(command, path)
        failed = (rc != 0 and "remote {0} already exists".format(remote_alias) not in stderr)
        logger.info("(work_remote): Successfully added remote path for local repository!")

    elif stdout != remote_path:
        # Repository has outdated remote path, updating...
        logger.warning("Remote ({0}) for local repository is outdated, updating...".format(remote_alias))
        command = ["git", "remote", "set-url", remote_alias, remote_path]

        logger.debug("(work_remote): command => {0}".format(str.join(" ", command)))
        (rc, stdout, stderr) = sh.subprocess_await(command, path)
        failed = (rc != 0 and "remote {0} already exists".format(remote_alias) not in stderr)
        logger.info("(work_remote): Successfully updated remote path for local repository!")

    # don't be tempted to remove the copy-paste job above; they only occur in 2/3 conditionals, not the else condition
    return (not failed)


def work_status(path):
    logger.debug("(work_status): Init")
    command = ["git", "status"]
    logger.debug("(work_status): command => {0}".format(str.join(" ", command)))
    (rc, stdout, stderr) = sh.subprocess_await(command, path)
    # logger.debug("(work_status): rc: {0}".format(rc))
    # if len(stdout) > 0: logger.info(str(stdout))
    # if len(stderr) > 0: logger.error(str(stderr))
    is_clean = ("nothing to commit, working directory clean" in stdout)
    # if not is_clean: return None
    return is_clean


def work_commit(path, message="Ansible auto-commit", initial=False):
    logger.debug("(work_commit): Init")
    if not initial:
        # # Check working directory status
        # status = work_status(path)
        # logger.debug("(work_commit): status is clean: {0}".format(status))

        # Stage working directory; copies files into '.git' directory
        # 'git add' detects all changes; 'git commit -a' only detects modified/deleted
        command = ["git", "add", "--all", "."]
        logger.debug("(work_commit): command => {0}".format(str.join(" ", command)))
        (rc, stdout, stderr) = sh.subprocess_await(command, path)
        # if len(stdout) > 0: logger.info(str(stdout))
        # if len(stderr) > 0: logger.error(str(stderr))
        # Commit the staged files
        command = ["git", "commit", "-m '{0}'".format(message)]
        logger.debug("(work_commit): command => {0}".format(str.join(" ", command)))
        (rc, stdout, stderr) = sh.subprocess_await(command, path)
        # if len(stdout) > 0: logger.info(str(stdout))
        # if len(stderr) > 0: logger.error(str(stderr))
        failed = (rc != 0 and "nothing to commit (working directory clean)" not in stdout)
        changed = (not failed and "nothing to commit (working directory clean)" not in stdout)
        return (not failed, changed)    # (succeeded, changed)
    else:
        # Initial commit for origin/master (fast-forward commit)
        # - pulls more reliable; helps prevent dangling HEAD refs
        # - HEAD initializes pointed to 'refs/heads/master'...
        #     but there's no true 'master' branch until first commit
        command = ["git", "commit", "--allow-empty", "-m 'Initial :: {0}'".format(message)]
        logger.debug("(work_commit): command => {0}".format(str.join(" ", command)))
        (rc, stdout, stderr) = sh.subprocess_await(command, path)
        return (True, True)             # (succeeded, changed)


# TODO: Set upstream (-u) on initial push; streamlines fetch
def work_push(path, version="master", remote_alias="origin"):
    logger.debug("(work_push): Init")
    command = ["git", "push", remote_alias, version]
    logger.debug("(work_push): command => {0}".format(str.join(" ", command)))
    (rc, stdout, stderr) = sh.subprocess_await(command, path)
    
    logger.debug("(work_push): rc: {0}".format(rc))
    if len(stdout) > 0: logger.info("(work_push): stdout: {0}".format(stdout))
    if len(stderr) > 0: logger.error("(work_push): stderr: {0}".format(stderr))

    failed = (rc != 0 and "Everything up-to-date" not in stderr)
    changed = (not failed and "Everything up-to-date" not in stderr)
    return (not failed, changed)


# --- Repository Metadata Reference Commands ---

# Trim extra apostrophes; expected format to validate against
def _ref_formatter(in_list):
    # logger.debug("(_ref_formatter): Init")
    # logger.debug("(_ref_formatter): in_list: {0}".format(in_list))
    results = [i.strip("'") for i in in_list]
    # logger.debug("(_ref_formatter): results: {0}".format(results))
    return results


def ref_head(path):
    # logger.debug("(ref_head): Init")
    command = ["git", "show-ref", "--head"]
    logger.debug("(ref_head): command => {0}".format(str.join(" ", command)))
    (rc, stdout, stderr) = sh.subprocess_await(command, path)
    # logger.debug("(ref_head): rc: {0}".format(rc))
    # if len(stdout) > 0: logger.info(str(stdout))
    # if len(stderr) > 0: logger.error(str(stderr))
    # failed = (rc != 0 and "Reinitialized existing Git repository" not in stdout)
    # changed = (not failed and "skipped, since" not in stdout)
    # return (not failed, changed)
    return stdout


# git for-each-ref --format='%(refname:short)' refs/heads
# git show-ref --heads      # decent but no formatting and rc=1 when empty
def ref_heads(path):
    # logger.debug("(ref_heads): Init")
    command = ["git", "for-each-ref", "--format='%(refname:short)'", "refs/heads"]
    logger.debug("(ref_heads): command => {0}".format(str.join(" ", command)))
    (rc, stdout, stderr) = sh.subprocess_await(command, path)
    # logger.debug("(ref_heads): rc: {0}".format(rc))
    # if len(stdout) > 0: logger.info(str(stdout))
    # if len(stderr) > 0: logger.error(str(stderr))
    stdout_lines = stdout.splitlines()
    # logger.debug("(ref_heads): stdout_lines: {0}".format(stdout_lines))
    results = _ref_formatter(stdout_lines)
    return results


# git for-each-ref --format='%(refname:short)' refs/remotes
# 'git for-each-ref' has better formatting than 'git branch -r'
def ref_remotes(path):
    # logger.debug("(ref_remotes): Init")
    command = ["git", "for-each-ref", "--format='%(refname:short)'", "refs/remotes"]
    logger.debug("(ref_remotes): command => {0}".format(str.join(" ", command)))
    (rc, stdout, stderr) = sh.subprocess_await(command, path)
    stdout_lines = stdout.splitlines()
    # logger.debug("(ref_remotes): stdout_lines: {0}".format(stdout_lines))
    results = _ref_formatter(stdout_lines)
    return results


# git for-each-ref --format='%(refname:short)' refs/tags
# git show-ref --tags       # decent but no formatting and rc=1 when empty
def ref_tags(path):
    # logger.debug("(ref_tags): Init")
    command = ["git", "for-each-ref", "--format='%(refname:short)'", "refs/tags"]
    logger.debug("(ref_tags): command => {0}".format(str.join(" ", command)))
    (rc, stdout, stderr) = sh.subprocess_await(command, path)
    stdout_lines = stdout.splitlines()
    # logger.debug("(ref_tags): stdout_lines: {0}".format(stdout_lines))
    results = _ref_formatter(stdout_lines)
    return results


# --- Repository (work) Branch Commands ---

# Validate version meets Git-allowed reference name rules
def branch_validate(version="master"):
    logger.debug("(branch_validate): Init")
    failed = False
    if version == "HEAD": return failed
    command = ["git", "check-ref-format", "--branch", version]
    logger.debug("(branch_validate): command => {0}".format(str.join(" ", command)))
    (rc, stdout, stderr) = sh.subprocess_await(command, path)
    logger.debug("(branch_validate): rc: {0}".format(rc))
    if len(stdout) > 0: logger.info(str(stdout))
    if len(stderr) > 0: logger.error(str(stderr))
    failed = (rc != 0 and "not a valid branch name" not in stderr)
    return (not failed)


# Providing 'remote_alias' will search in remotes instead of heads
def branch_exists(path, version="master", remote_alias=""):
    logger.debug("(branch_exists): Init")
    is_remote = bool(remote_alias)
    verify_branch = "{0}/{1}".format(remote_alias, version) if is_remote else version
    # Determine which metadata to check for branch list
    ref_method = ref_remotes if is_remote else ref_heads
    branch_results = ref_method(path)
    # Check branch version exists in branch list
    logger.debug("(branch_exists): current branches: {0}".format(branch_results))
    is_found = (verify_branch in branch_results)
    logger.debug("(branch_exists): branch '{0}' is found: {1}".format(verify_branch, is_found))
    return is_found


def branch_create(path, version="master"):
    logger.debug("(branch_create): Init")
    # 'git branch --force' resets the branch's HEAD (not wanted)
    command = ["git", "branch", version]
    logger.debug("(branch_create): command => {0}".format(str.join(" ", command)))
    (rc, stdout, stderr) = sh.subprocess_await(command, path)
    # logger.debug("(branch_create): rc: {0}".format(rc))
    # if len(stdout) > 0: logger.info(str(stdout))
    # if len(stderr) > 0: logger.error(str(stderr))
    failed = (rc != 0 and "already exists" not in stderr)
    changed = (not failed and "already exists" not in stderr)
    logger.debug("(branch_create): succeeded: {0}, changed: {1}".format(not failed, changed))
    return (not failed, changed)


# TODO: option to call exists and create
def branch_switch(path, version="master"):
    logger.debug("(branch_switch): Init")
    # 'git branch --force' resets the branch's HEAD (not wanted)
    command = ["git", "checkout", version]
    logger.debug("(branch_switch): command => {0}".format(str.join(" ", command)))
    (rc, stdout, stderr) = sh.subprocess_await(command, path)
    changed = ("Already on" not in stderr)
    return changed


# Supports either local or remote paths
def branch_delete(path, version="master"):
    logger.debug("(branch_delete): Init")
    command = ["git", "branch", "-D {0}".format(version)]
    logger.debug("(branch_delete): command => {0}".format(str.join(" ", command)))
    (rc, stdout, stderr) = sh.subprocess_await(command, path)
    if len(stdout) > 0: logger.info(str(stdout))
    if len(stderr) > 0: logger.error(str(stderr))

    failed = (rc != 0)
    changed = (not failed and "Deleted branch" in stdout)
    logger.debug("(branch_delete): succeeded: {0}, changed: {1}".format(not failed, changed))
    return (not failed, changed)


# --- Repository (work) Pull Commands ---

# Fetch the latest meta data; increases '.git' directory size
def work_fetch(path, remote_alias="origin"):
    # logger.debug("(work_fetch): Init")
    command = ["git", "fetch", "--prune", remote_alias]
    logger.debug("(work_fetch): command => {0}".format(str.join(" ", command)))
    (rc, stdout, stderr) = sh.subprocess_await(command, path)
    failed = (rc != 0 and "find remote ref" not in stdout)
    changed = (not failed and "find remote ref" not in stdout and "Everything up-to-date" not in stderr)
    return (not failed, changed)


# other pull_type choice is 'theirs'
def work_merge(path, version="master", remote_alias="origin", fast_forward=True, pull_type="ours"):
    logger.debug("(work_merge): Init")
    # Merge pull branch (auto-resolve)
    remote_branch = "{0}/{1}".format(remote_alias, version)
    command = ["git", "merge", remote_branch]
    if not fast_forward: command.append("--no-ff")
    command.extend(["--strategy=recursive", "--strategy-option={0}".format(pull_type), "-m 'Ansible auto-merge'"])
    logger.debug("(work_merge): command => {0}".format(str.join(" ", command)))
    (rc, stdout, stderr) = sh.subprocess_await(command, path)
    
    logger.debug("(work_merge): rc: {0}".format(rc))
    if len(stdout) > 0: logger.info("(work_merge): stdout: {0}".format(stdout))
    if len(stderr) > 0: logger.error("(work_merge): stderr: {0}".format(stderr))

    changed = ("Already uptodate" not in stdout and "Already up-to-date" not in stdout)
    return changed


def work_rebase(path, version="master", remote_alias="origin"):
    logger.debug("(work_rebase): Init")
    # Merge pull branch (auto-resolve)
    remote_branch = "{0}/{1}".format(remote_alias, version)
    command = ["git", "rebase", remote_branch]
    logger.debug("(work_rebase): command => {0}".format(str.join(" ", command)))
    (rc, stdout, stderr) = sh.subprocess_await(command, path)
    # logger.debug("(work_rebase): rc: {0}".format(rc))
    # if len(stdout) > 0: logger.info("(work_rebase): stdout: {0}".format(stdout))
    # if len(stderr) > 0: logger.error("(work_rebase): stderr: {0}".format(stderr))
    failed = (rc != 0)
    changed = (not failed and "is up to date" not in stdout)
    return (not failed, changed)


def work_reset(path, version="master", remote_alias="origin"):
    logger.debug("(work_reset): Init")
    # Reset branch to latest (auto-resolve)
    remote_branch = "{0}/{1}".format(remote_alias, version)
    command = ["git", "reset", "--hard", remote_branch]
    logger.debug("(work_reset): command => {0}".format(str.join(" ", command)))
    (rc, stdout, stderr) = sh.subprocess_await(command, path)
    
    logger.debug("(work_reset): rc: {0}".format(rc))
    if len(stdout) > 0: logger.info(str(stdout))
    if len(stderr) > 0: logger.error(str(stderr))

    return (rc == 0)


# ------------------------ Primary Classes ------------------------

class Repository(object):
    def __init__(self, path, remote_path="", skip_create=False, force=False):
        # logger.debug("(Repository:__init__): Init")
        self.path = str(path)
        self.remote_path = str(remote_path) if remote_path else ""
        self.force = bool(force)
        self.is_bare = not bool(self.remote_path)
        self.repo_descriptor = "remote, bare" if self.is_bare else "local, work"

        self.exists = repo_exists(self.path, self.is_bare)
        if self.exists:
            logger.debug("(Repository:__init__): Successfully found {0} repository".format(self.repo_descriptor))
        else:
            logger.debug("(Repository:__init__): Unable to locate {0} repository".format(self.repo_descriptor))
            if self.is_bare:
                if not skip_create: self.create()
            else:
                # Create repository whenever missing
                self.create()


    def create(self):
        logger.debug("(Repository:create): Init")
        if not self.force:
            response = raw_input("Repository not found ({0}/.git), initialize?  (y or yes):".format(self.path))
            if response.lower() not in ["", "y", "yes"]:
                logger.info("Exiting without creating repository")
                sh.process_fail()
        else:
            logger.info("Repository not found ({0}/.git), initializing...".format(self.path))
        
        # Initialize the repository
        (self.exists, changed) = repo_create(self.path, self.is_bare)
        if self.exists:
            logger.info("Repository successfully created!")
        else:
            logger.error("(Repository:create): Unable to create {0} repository".format(self.repo_descriptor))
            sh.process_fail()


# ------------------------ Main Program ------------------------

# Initialize the logger
basename = "git_boilerplate"
log_options = LogOptions(basename)
logger = get_logger(log_options)

if __name__ == "__main__":
    def parse_arguments():
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--debug", action="store_true")
        parser.add_argument("--test", choices=["subprocess", "multiprocess", "xml"])
        return parser.parse_args()
    args = parse_arguments()

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
        logger.debug("(__main__): Validation command => {0}".format(str.join(" ", validatorCmd)))

        # Validate configuration against the schema
        # (rc, stdout, stderr) = subprocess_await(validatorCmd, stdout_log=logger, stderr_log=logger)
        (rc, stdout, stderr) = subprocess_await(validatorCmd)
        if rc != 0:
            logger.error("(__main__): XML file ({0}) failed to validate against schema ({1})".format(config_xml, config_xsd))
            subprocess_print(logger, rc, stdout, stderr, validatorCmd)
        else:
            logger.debug("(__main__): {0} was successfully validated".format(xmlPath))


    # --- Usage Example ---
    # sudo python /root/.local/lib/python2.7/site-packages/git_boilerplate.py
    # sudo python /root/.local/lib/python2.7/site-packages/git_boilerplate.py --debug --test=subprocess
