#!/usr/bin/python

# Basename: mygit
# Description: A service to control common Git business logic
# Version: 1.1.0
# VersionDate: 4 Sep 2020

# 		*** Actions ***
# push: 				Either pull or create a bare repository; then push
# pull: 				Auto-resolve using 'ours' merge strategy; favors existing changes
# reset:				Disregard existing working directory changes; match files to remote
# status:				Determines whether the work-tree is clean (True) or dirty (False)
# delete:				Removes the specified branch in locl and remote repositories
# 		*** Options ***
# --debug: 				Enable to display log messages for development
# --force:				Enable to disregard the initialize repository prompt
# --branch: 			Arbitrary name of branch to push/pull
# --gitignore-path:		Location of .gitignore file to use
# --remote-alias:		Alias used for bare repo; default is 'origin'
# --remote-path:		Remote, bare repository path (origin)
# --local-path:			Specify where to create work repo; default is current directory

from logging_boilerplate import *
import shell_boilerplate as sh
import git_boilerplate as bp_git

try:
    # Python 2 has both 'str' (bytes) and 'unicode' text
    basestring = basestring
    unicode = unicode
except NameError:
    # Python 3 names the unicode data type 'str'
    basestring = str
    unicode = str

# ------------------------ Primary classes/functions ------------------------

class Repository(object):
	def __init__(self, path, remote_path="", no_create=False, force=False):
		# logger.debug("(Repository:__init__): Init")
		self.path = str(path)
		self.remote_path = str(remote_path) if remote_path else ""
		self.force = bool(force)
		self.is_bare = not bool(self.remote_path)
		self.repo_descriptor = "remote, bare" if self.is_bare else "local, work"

		self.exists = bp_git.repo_exists(self.path, self.is_bare)
		if self.exists:
			logger.debug("(Repository:__init__): Successfully found {0} repository".format(self.repo_descriptor))
		else:
			logger.debug("(Repository:__init__): Unable to locate {0} repository".format(self.repo_descriptor))
			if not no_create:
				self.create()
			else:
				logger.error("(Repository:__init__): Cannot proceed; missing {0} repository".format(self.repo_descriptor))
				sh.process_fail()


	def create(self):
		# logger.debug("(Repository:create): Init")
		display_path = self.path if (self.is_bare) else "{0}/.git".format(self.path)
		if not self.force:
			response = raw_input("Repository not found ({0}), initialize?  (y or yes): ".format(display_path))
			if response.lower() not in ["y", "yes"]:
				logger.info("Exiting without creating repository")
				sh.process_fail()
		else:
			logger.info("Repository not found ({0}), initializing...".format(display_path))
		
		# Initialize the repository
		(self.exists, changed) = bp_git.repo_create(self.path, self.is_bare)
		if self.exists:
			logger.info("Repository successfully created!")
		else:
			logger.error("(Repository:create): Unable to create {0} repository".format(self.repo_descriptor))
			sh.process_fail()



class GitController(object):
	def __init__(self):
		# logger.debug("(GitController:__init__): Init")
		logger.debug("args: {0}".format(args))
		logger.info("Git '{0}' action detected".format(args.action))
		logger.debug("--------------------------------------------------------")


		# ------------------------ Primary business logic area ------------------------

		# *** STEP 01) Ensure bare repo exists

		# ------------------------ Remote, bare repository ------------------------

		if (args.action in ["status", "reset"]):
			logger.debug("(GitController:__init__): skip bare repository check for '{0}' action".format(args.action))
		else:
			no_create = (args.action != "push") # fail when not 'push' action and repo missing
			self.bare_repository = Repository(args.remote_path, no_create=no_create, force=True)
			logger.debug("(GitController:__init__): bare_repository exists: {0}".format(self.bare_repository.exists))


		# *** STEP 02) Ensure work repo exists

		# ------------------------ Local, work repository ------------------------
		no_create = (args.action != "push") # fail when not 'push' action and repo missing
		self.work_repository = Repository(args.local_path, args.remote_path, no_create=no_create, force=True)
		logger.debug("(GitController:__init__): work_repository exists: {0}".format(self.work_repository.exists))


		# *** STEP 03) Set work repo's remote path to bare repository

		remote_result = bp_git.work_remote(args.local_path, args.remote_path, args.remote_alias)
		if not remote_result:
			logger.error("(GitController:__init__): Error occurred updating remote path")
			sh.process_fail()


		# *** STEP 04) Fetch latest meta data

		# Fetch the latest meta data; increases '.git' directory size
		if args.action in ["push", "pull"]:
			meta_result = bp_git.work_fetch(args.local_path)
			if not meta_result:
				# TODO: maybe remove after testing - never expect this to run with checks above
				logger.error("(GitController:__init__): Error occurred fetching metadata references")
				sh.process_fail()


		# ------------------------ Validation Checks ------------------------

		logger.debug("---------------- Validation Checks ----------------")

		# Check work-tree status
		work_tree_is_clean = bp_git.work_status(args.local_path)
		logger.debug("(GitController:__init__): work-tree is clean: {0}".format(work_tree_is_clean))
		# Gather cache of branch names (fewer queries to refs)
		local_branches = bp_git.branch_list(args.local_path)
		remote_branches = bp_git.branch_list(args.local_path, args.remote_alias)
		# Check for branches in 'refs/heads' and 'refs/remotes'
		master_local_branch_exists = bp_git.branch_exists(args.local_path, master_branch, branches=local_branches)
		master_remote_branch_exists = bp_git.branch_exists(args.local_path, master_branch, args.remote_alias, branches=remote_branches)
		logger.debug("(GitController:__init__): master_local_branch_exists: {0}".format(master_local_branch_exists))
		logger.debug("(GitController:__init__): master_remote_branch_exists: {0}".format(master_remote_branch_exists))
		stash_local_branch_exists = bp_git.branch_exists(args.local_path, stash_branch, branches=local_branches)
		logger.debug("(GitController:__init__): stash_local_branch_exists: {0}".format(stash_local_branch_exists))
		version_local_branch_exists = bp_git.branch_exists(args.local_path, args.branch, branches=local_branches)
		version_remote_branch_exists = bp_git.branch_exists(args.local_path, args.branch, args.remote_alias, branches=remote_branches)
		logger.debug("(GitController:__init__): version_local_branch_exists: {0}".format(version_local_branch_exists))
		logger.debug("(GitController:__init__): version_remote_branch_exists: {0}".format(version_remote_branch_exists))

		# Fail early when attempting to pull/delete a dirty work-tree
		if args.action in ["pull", "delete"] and not work_tree_is_clean:
			logger.error("(GitController:__init__): Unable to perform '{0}' action with dirty work-tree".format(args.action))
			sh.process_fail()

		# Fail early when attempting to delete 'master' branch; assumed to always exist after initial commit
		if args.action == "delete" and args.branch == master_branch:
			logger.error("(GitController:__init__): Unable to delete the '{0}' branch".format(master_branch))
			sh.process_fail()

		# Fail early when attempting to pull 'master' or 'version' branch that's missing from bare repo
		if args.action == "pull":
			if not master_remote_branch_exists:
				logger.error("(GitController:__init__): Unable to perform '{0}' action; '{1}/{2}' branch not found".format(args.action, args.remote_alias, master_branch))
				sh.process_fail()
			if not version_remote_branch_exists:
				logger.error("(GitController:__init__): Unable to perform '{0}' action; '{1}/{2}' branch not found".format(args.action, args.remote_alias, args.branch))
				sh.process_fail()


		# ------------------------ 'master' branch ------------------------

		logger.debug("---------------- Master Branch Steps ----------------")

		# 'master' branch should always exist; regardless whether it's the focus of this run
		if args.action in ["push", "pull"] and not master_local_branch_exists:
			if master_remote_branch_exists:
				# Switch to bare repository 'master' branch before any commits
				bp_git.branch_switch(args.local_path, master_branch, args.remote_alias)
				logger.debug("(GitController:__init__): checked out '{0}/{1}' branch".format(args.remote_alias, master_branch))
				master_local_branch_exists = bp_git.branch_create(args.local_path, master_branch)
				logger.debug("(GitController:__init__): created local '{1}' branch from remote '{0}/{1}' branch".format(args.remote_alias, master_branch))
			else:
				# Push initial 'master' branch to remote when not already there
				logger.warning("(GitController:__init__): '{0}' branch is missing, creating initial commit...".format(master_branch))
				(commit_succeeded, commit_changed) = bp_git.work_commit(args.local_path, initial=True)
				logger.info("Intial commit for '{0}' branch successfully created!".format(master_branch))
				# 'master' branch automatically active after initial commit; explicit checkout unnecessary

				(push_succeeded, push_changed) = bp_git.work_push(args.local_path, master_branch, args.remote_alias)
				logger.debug("(GitController:__init__): initial push to '{0}/{1}' has succeeded: {2}".format(args.remote_alias, master_branch, push_succeeded))
				# No need to refresh metadata again; push will update references


		# ------------------------ 'my-stash' branch ------------------------

		logger.debug("---------------- Stash Branch Steps ----------------")

		# When work-tree is dirty, commit the changes to 'my-stash' branch
		if args.action == "push" and version_remote_branch_exists and not work_tree_is_clean:
			logger.debug("(GitController:__init__): preparing to stash work-tree changes...")

			# Create 'my-stash' branch from local 'master' branch
			bp_git.branch_switch(args.local_path, master_branch)
			logger.debug("(GitController:__init__): checked out '{0}' branch".format(master_branch))

			# Check if stash branch already exists, delete if so
			if stash_local_branch_exists:
				logger.debug("(GitController:__init__): previous '{0}' branch was detected, removing...".format(work_tree_is_clean))
				bp_git.branch_delete(args.local_path, stash_branch)
				logger.debug("(GitController:__init__): '{0}' branch was deleted".format(work_tree_is_clean))

			# Create and checkout 'my-stash' branch to stage and commit those dirty files
			stash_local_branch_exists = bp_git.branch_create(args.local_path, stash_branch)
			bp_git.branch_switch(args.local_path, stash_branch)
			logger.debug("(GitController:__init__): created and checked out '{0}' branch".format(stash_branch))
			(commit_succeeded, commit_changed) = bp_git.work_commit(args.local_path)
			logger.debug("(GitController:__init__): commit for '{0}' branch succeeded: {1}".format(stash_branch, commit_succeeded))

			# Verify work-tree status (should always be clean after commit)
			work_tree_is_clean = bp_git.work_status(args.local_path)
			logger.debug("(GitController:__init__): work-tree is clean: {0}".format(work_tree_is_clean))


		# ------------------------ 'version' branch ------------------------

		logger.debug("---------------- Version Branch Steps ----------------")
		# -------- Avoid checkout of branch until work-tree is clean --------

		# Create local 'version' branch if missing
		if args.action in ["push", "pull"]:
			version_branch_just_created = False
			if not version_local_branch_exists:
				if version_remote_branch_exists:
					# Create local 'version' branch from bare repository
					bp_git.branch_switch(args.local_path, args.branch, args.remote_alias)
					logger.debug("(GitController:__init__): checked out '{0}/{1}' branch".format(args.remote_alias, args.branch))
					version_local_branch_exists = bp_git.branch_create(args.local_path, args.branch)
					logger.debug("(GitController:__init__): created local '{1}' branch from remote '{0}/{1}' branch".format(args.remote_alias, args.branch))
				else:
					# Create local 'version' branch from 'master' branch
					bp_git.branch_switch(args.local_path, master_branch)
					logger.debug("(GitController:__init__): checked out '{0}' branch".format(master_branch))
					version_local_branch_exists = bp_git.branch_create(args.local_path, args.branch)
					logger.debug("(GitController:__init__): created local '{1}' branch from '{0}' branch".format(master_branch, args.branch))
					version_branch_just_created = True
					# Verify successfully created 'version' branch
					if not version_local_branch_exists:
						logger.error("(GitController:__init__): local '{0}' branch still appears to be missing; failed to create".format(args.branch))
						sh.process_fail()
				
				# Checkout local 'version' branch
				bp_git.branch_switch(args.local_path, args.branch)


			# Commit changes to local 'version' branch; not using 'my-stash' branch because remote 'version' branch is missing
			if args.action == "push":
				# When work-tree is dirty, commit changes to 'version' branch
				if not work_tree_is_clean and not version_remote_branch_exists:
					(commit_succeeded, commit_changed) = bp_git.work_commit(args.local_path)
					logger.debug("(GitController:__init__): commit for '{0}' branch succeeded: {1}".format(args.branch, commit_succeeded))
					# Verify work-tree status (should always be clean after commit)
					work_tree_is_clean = bp_git.work_status(args.local_path)
			

			# Merge remote 'version' branch into local when both exist and local wasn't just created
			if args.action in ["push", "pull"]:
				if version_remote_branch_exists and not version_branch_just_created:
					# Merge 'version' branch from bare repository into local
					logger.debug("(GitController:__init__): merge '{0}/{1}' branch into local '{0}' branch".format(args.remote_alias, args.branch))
					(succeeded, changed) = bp_git.work_merge(args.local_path, args.branch, args.remote_alias)
					logger.debug("(GitController:__init__): '{0}/{1}' branch merge succeeded: {2}".format(args.remote_alias, args.branch, succeeded))


			# Rebase local 'my-stash' branch onto local 'version' branch
			if args.action == "push" and stash_local_branch_exists:
				bp_git.branch_switch(args.local_path, stash_branch)
				logger.debug("(GitController:__init__): checked out '{0}' branch".format(stash_branch))
				logger.debug("(GitController:__init__): rebasing '{0}' branch onto local '{1}' branch".format(stash_branch, args.branch))
				(succeeded, changed) = bp_git.work_rebase(args.local_path, args.branch)
				logger.debug("(GitController:__init__): '{0}' branch rebase succeeded: {1}".format(stash_branch, succeeded))
				# Checkout local 'version' branch
				bp_git.branch_switch(args.local_path, args.branch)
				# Delete 'my-stash' branch
				bp_git.branch_delete(args.local_path, stash_branch)


		# TODO: other action steps
		if args.action == "reset":
			# Hard reset will also clear any pending (unpushed) commits
			logger.info("(GitController:__init__): ::mock:: reset action")
			bp_git.work_reset(args.local_path, args.branch, args.remote_alias)

		elif args.action == "delete":
			# Deleting both local and remote branches, no pull steps needed
			logger.debug("(GitController:__init__): deleting '{0}' branch...".format(args.branch))
			# Checkout local 'master' branch
			bp_git.branch_switch(args.local_path, master_branch)
			# Delete 'version' branch
			bp_git.branch_delete(args.local_path, args.branch)
			bp_git.branch_delete(args.remote_path, args.branch)
			logger.debug("(GitController:__init__): '{0}' branch deleted".format(args.branch))

		elif args.action == "status":
			# Verify work-tree status and display status statement
			work_tree_is_clean = bp_git.work_status(args.local_path)
			logger.info("work_tree_is_clean: {0}".format(work_tree_is_clean))


		# *** STEP 07) Push to bare repository

		if args.action == "push":
			# Push 'version' branch to bare repository
			logger.debug("(GitController:__init__): pushing '{0}' branch to {1}".format(args.branch, args.remote_alias))
			(push_succeeded, push_changed) = bp_git.work_push(args.local_path, args.branch, args.remote_alias)
			logger.debug("(GitController:__init__): '{0}/{1}' branch push has succeeded: {2}".format(args.remote_alias, args.branch, push_succeeded))
			# No need to refresh metadata again; push will update references



# ------------------------ Main program ------------------------

master_branch = "master"
stash_branch = "my-stash"

# Initialize the logger
basename = "mygit"
log_file = "/var/log/{0}.log".format(basename)
log_options = LogOptions(basename)
logger = get_logger(log_options)

if __name__ = "__main__":
    def parse_arguments():
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("action", choices=["push", "pull", "reset", "status", "delete"])
        parser.add_argument("--debug", action="store_true")
        parser.add_argument("--force", "-f", action="store_true")
        parser.add_argument("--remote-path", default="$HOME/my_origin_repo.git")
        parser.add_argument("--local-path", default=sh.path_current())
        parser.add_argument("--branch", "-b", default=master_branch)
        parser.add_argument("--remote-alias", default="origin")
        parser.add_argument("--gitignore-path", default="")
        return parser.parse_args()
    args = parse_arguments()

    # Configure the logger
    log_level = 20                  # logging.INFO
    if args.debug: log_level = 10   # logging.DEBUG
    logger.setLevel(log_level)

	# Configure the git_boilerplate logger
	if args.debug:
		git_logger = get_logger("git_boilerplate")
		git_logger.setLevel(log_level)

	controller = GitController()

	# If we get to this point, assume all went well
	logger.debug("--------------------------------------------------------")
	logger.debug("--- end point reached :3 ---")
	sh.process_exit()


	# :: Usage Example ::
	# mygit push --branch="Zoolander"
	# mygit push --debug --force --branch="Zoolander" --gitignore-path="$HOME/.gitignore"
