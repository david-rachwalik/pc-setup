#!/usr/bin/env python

# Basename: git_boilerplate
# Description: Common business logic for Git (v1.8.x)
# Version: 1.3.0
# VersionDate: 5 Feb 2021

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

# ------------------------ Global Commands ------------------------

# --- Repository (bare/work) Commands ---

def repo_exists(path, bare=False):
    result = False
    if bare:
        if sh.path_exists(path, "d"):
            command = ["git", "rev-parse", "--is-bare-repository"]
            sh.print_command(command)
            (stdout, stderr, rc) = sh.subprocess_run(command, path)
            # sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
            result = (rc == 0 and stdout == "true")
    else:
        work_repo_dir = sh.path_join(path, ".git")
        result = sh.path_exists(work_repo_dir, "d")
    return result


# Initialize the repository
def repo_create(path, bare=False):
    command = ["git", "init"]
    if bare:
        sh.directory_create(path) # Directory must exist prior
        command.append("--bare")
    sh.print_command(command)
    (stdout, stderr, rc) = sh.subprocess_run(command, path)
    sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
    failed = (rc != 0 and "Reinitialized existing Git repository" not in stdout)
    changed = (not failed and "skipped, since" not in stdout)
    return (not failed, changed)


# --- Repository (work) Commands ---

# Ensure remote path links to bare repository
def work_remote(path, remote_path, remote_alias="origin"):
    failed = False
    # Check local repository for remote alias
    command = ["git", "config", "--get", "remote.{0}.url".format(remote_alias)]
    (stdout, stderr, rc) = sh.subprocess_run(command, path)
    if not stdout:
        # Repository is missing remote path, adding...
        _log.warning("Remote ({0}) for local repository is missing, adding...".format(remote_alias))
        command = ["git", "remote", "add", remote_alias, remote_path]

        sh.print_command(command)
        (stdout, stderr, rc) = sh.subprocess_run(command, path)
        failed = (rc != 0 and "remote {0} already exists".format(remote_alias) not in stderr)
        _log.info("(work_remote): Successfully added remote path for local repository!")

    elif stdout != remote_path:
        # Repository has outdated remote path, updating...
        _log.warning("Remote ({0}) for local repository is outdated, updating...".format(remote_alias))
        command = ["git", "remote", "set-url", remote_alias, remote_path]

        sh.print_command(command)
        (stdout, stderr, rc) = sh.subprocess_run(command, path)
        failed = (rc != 0 and "remote {0} already exists".format(remote_alias) not in stderr)
        _log.info("(work_remote): Successfully updated remote path for local repository!")

    # don't be tempted to remove the copy-paste job above; they only occur in 2/3 conditionals, not the else condition
    return (not failed)


def work_status(path):
    command = ["git", "status"]
    sh.print_command(command)
    (stdout, stderr, rc) = sh.subprocess_run(command, path)
    # sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
    is_clean = ("nothing to commit, working directory clean" in stdout)
    return is_clean


def work_commit(path, message="auto-commit", initial=False):
    if not initial:
        # Stage working directory; copies files into '.git' directory
        # 'git add' detects all changes; 'git commit -a' only detects modified/deleted
        command = ["git", "add", "--all", "."]
        sh.print_command(command)
        (stdout, stderr, rc) = sh.subprocess_run(command, path)
        # sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)

        # Commit the staged files
        command = ["git", "commit", "-m '{0}'".format(message)]
        sh.print_command(command)
        (stdout, stderr, rc) = sh.subprocess_run(command, path)
        # sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
        failed = (rc != 0 and "nothing to commit (working directory clean)" not in stdout)
        changed = (not failed and "nothing to commit (working directory clean)" not in stdout)
        return (not failed, changed)    # (succeeded, changed)
    else:
        # Initial commit so 'master' branch exists; helps prevent dangling HEAD refs
        # - HEAD points to 'refs/heads/master' after 'git init'
        # - however, there's no true 'master' branch until the first commit
        command = ["git", "commit", "--allow-empty", "-m 'Initial {0}'".format(message)]
        sh.print_command(command)
        (stdout, stderr, rc) = sh.subprocess_run(command, path)
        return (True, True)             # (succeeded, changed)


# TODO: Set upstream (-u) on initial push; streamlines fetch
def work_push(path, version="master", remote_alias="origin"):
    command = ["git", "push", remote_alias, version]
    sh.print_command(command)
    (stdout, stderr, rc) = sh.subprocess_run(command, path)
    sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
    failed = (rc != 0 and "Everything up-to-date" not in stderr)
    changed = (not failed and "Everything up-to-date" not in stderr)
    return (not failed, changed)


# --- Repository Metadata Reference Commands ---

# Trim extra apostrophes; expected format to validate against
def _ref_formatter(in_list):
    # _log.debug("(_ref_formatter): in_list: {0}".format(in_list))
    results = [i.strip("'") for i in in_list]
    # _log.debug("(_ref_formatter): results: {0}".format(results))
    return results


def ref_head(path):
    # command = ["git", "show-ref", "--head"]
    command = ["git", "rev-parse", "--abbrev-ref", "HEAD"]
    sh.print_command(command)
    (stdout, stderr, rc) = sh.subprocess_run(command, path)
    # sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
    result = stdout if (rc == 0) else ""
    return result


# git for-each-ref --format='%(refname:short)' refs/heads
# git show-ref --heads      # decent but no formatting and rc=1 when empty
def ref_heads(path):
    command = ["git", "for-each-ref", "--format='%(refname:short)'", "refs/heads"]
    sh.print_command(command)
    (stdout, stderr, rc) = sh.subprocess_run(command, path)
    # sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
    stdout_lines = stdout.splitlines()
    # _log.debug("(ref_heads): stdout_lines: {0}".format(stdout_lines))
    results = _ref_formatter(stdout_lines)
    return results


# git for-each-ref --format='%(refname:short)' refs/remotes
# 'git for-each-ref' has better formatting than 'git branch -r'
def ref_remotes(path):
    command = ["git", "for-each-ref", "--format='%(refname:short)'", "refs/remotes"]
    sh.print_command(command)
    (stdout, stderr, rc) = sh.subprocess_run(command, path)
    # sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
    stdout_lines = stdout.splitlines()
    # _log.debug("(ref_remotes): stdout_lines: {0}".format(stdout_lines))
    results = _ref_formatter(stdout_lines)
    return results


# git for-each-ref --format='%(refname:short)' refs/tags
# git show-ref --tags       # decent but no formatting and rc=1 when empty
def ref_tags(path):
    command = ["git", "for-each-ref", "--format='%(refname:short)'", "refs/tags"]
    sh.print_command(command)
    (stdout, stderr, rc) = sh.subprocess_run(command, path)
    # sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
    stdout_lines = stdout.splitlines()
    # _log.debug("(ref_tags): stdout_lines: {0}".format(stdout_lines))
    results = _ref_formatter(stdout_lines)
    return results


# --- Repository (work) Branch Commands ---

# Validate version meets Git-allowed reference name rules
def branch_validate(version="master"):
    failed = False
    if version == "HEAD": return failed
    command = ["git", "check-ref-format", "--branch", version]
    sh.print_command(command)
    (stdout, stderr, rc) = sh.subprocess_run(command, path)
    sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
    failed = (rc != 0 and "not a valid branch name" not in stderr)
    return (not failed)


# Providing 'remote_alias' will search in remotes instead of heads
def branch_list(path, remote_alias=""):
    # Determine which metadata to check for branch list
    ref_method = ref_remotes if remote_alias else ref_heads
    branch_results = ref_method(path)
    ref_descriptor = "remote" if remote_alias else "local"
    _log.debug("(branch_list): branches: ({0}): {1}".format(ref_descriptor, branch_results))
    return branch_results


# Providing 'remote_alias' will search in remotes instead of heads
# - 'branches' expects list of strings; omit to automatically call branch_list
def branch_exists(path, version="master", remote_alias="", branches=None):
    remote_branch = "{0}/{1}".format(remote_alias, version)
    use_branch = remote_branch if remote_alias else version
    # Gather cache of branch names
    if isinstance(branches, list):
        branch_results = branches
    else:
        branch_results = branch_list(path, remote_alias)
    # Check branch version exists in branch list
    # _log.debug("(branch_exists): branches: {0}".format(branch_results))
    is_found = (use_branch in branch_results)
    _log.debug("(branch_exists): branch '{0}' is found: {1}".format(use_branch, is_found))
    return is_found


def branch_create(path, version="master"):
    # 'git branch --force' resets the branch's HEAD (not wanted)
    command = ["git", "branch", version]
    sh.print_command(command)
    (stdout, stderr, rc) = sh.subprocess_run(command, path)
    # sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
    failed = (rc != 0 and "already exists" not in stderr)
    changed = (not failed and "already exists" not in stderr)
    # _log.debug("(branch_create): succeeded: {0}, changed: {1}".format(not failed, changed))
    return (not failed, changed)


# TODO: option to call exists and create
def branch_switch(path, version="master", remote_alias=""):
    remote_branch = "{0}/{1}".format(remote_alias, version)
    use_branch = remote_branch if remote_alias else version
    command = ["git", "checkout", use_branch]
    sh.print_command(command)
    (stdout, stderr, rc) = sh.subprocess_run(command, path)
    # sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
    failed = (rc != 0)
    changed = (not failed and "Already on" not in stderr)
    return (not failed, changed)


# Supports either local or remote paths
def branch_delete(path, version="master"):
    command = ["git", "branch", "-D", version]
    sh.print_command(command)
    (stdout, stderr, rc) = sh.subprocess_run(command, path)
    sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
    failed = (rc != 0)
    changed = (not failed and "Deleted branch" in stdout)
    _log.debug("(branch_delete): succeeded: {0}, changed: {1}".format(not failed, changed))
    return (not failed, changed)


# --- Repository (work) Pull Commands ---

# Fetch the latest meta data; increases '.git' directory size
# Consider 'git fetch --all' https://www.atlassian.com/git/tutorials/syncing/git-fetch
def work_fetch(path, remote_alias="origin"):
    command = ["git", "fetch", "--prune", remote_alias]
    sh.print_command(command)
    (stdout, stderr, rc) = sh.subprocess_run(command, path)
    failed = (rc != 0 and "find remote ref" not in stdout)
    changed = (not failed and "find remote ref" not in stdout and "Everything up-to-date" not in stderr)
    return (not failed, changed)


# other pull_type choice is 'theirs'; message for potential merge commit
def work_merge(path, version="master", remote_alias="", message="auto-merge", fast_forward=True, pull_type="ours"):
    # Merge pull branch (auto-resolve)
    remote_branch = "{0}/{1}".format(remote_alias, version)
    use_branch = remote_branch if remote_alias else version
    command = ["git", "merge", use_branch]
    if not fast_forward: command.append("--no-ff")
    command.extend(["--strategy=recursive", "--strategy-option={0}".format(pull_type), "-m '{0}'".format(message)])
    sh.print_command(command)
    (stdout, stderr, rc) = sh.subprocess_run(command, path)
    # sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
    failed = (rc != 0)
    changed = (not failed and "Already uptodate" not in stdout and "Already up-to-date" not in stdout)
    return (not failed, changed)


# Rebase replays commits from currently active branch onto 'version' parameter target branch
# - automatically uses default of --strategy='recursive' --strategy-option='theirs'
# - ours/theirs is reverse of merge; theirs is currently active branch - ours is target branch
# - 'remote_alias' parameter not implemented so rebase is only used for local work (e.g. feature branch)
def work_rebase(path, version="master"):
    # Merge pull branch (auto-resolve)
    command = ["git", "rebase", version]
    sh.print_command(command)
    (stdout, stderr, rc) = sh.subprocess_run(command, path)
    # sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
    failed = (rc != 0)
    changed = (not failed and "is up to date" not in stdout)
    return (not failed, changed)


# Reset branch to latest (auto-resolve)
def work_reset(path, version="master", remote_alias=""):
    remote_branch = "{0}/{1}".format(remote_alias, version)
    use_branch = remote_branch if remote_alias else version
    command = ["git", "reset", "--hard", use_branch]
    sh.print_command(command)
    (stdout, stderr, rc) = sh.subprocess_run(command, path)
    # sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
    return (rc == 0)


# ------------------------ Main Program ------------------------

# Initialize the logger
basename = "git_boilerplate"
args = LogArgs() # for external modules
log_options = LogOptions(basename)
_log = get_logger(log_options)

if __name__ == "__main__":
    def parse_arguments():
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--debug", action="store_true")
        return parser.parse_args()
    args = parse_arguments()

    #  Configure the main logger
    log_handlers = gen_basic_handlers(args.debug, args.log_path)
    set_handlers(_log, log_handlers)
    if args.debug:
        # Configure the shell_boilerplate logger
        _sh_log = get_logger("shell_boilerplate")
        set_handlers(_sh_log, log_handlers)
        sh.args.debug = args.debug

    _log.debug("args: {0}".format(args))
    _log.debug("------------------------------------------------")


    # --- Usage Example ---
    # python ~/.local/lib/python3.6/site-packages/git_boilerplate.py --debug --test=subprocess
