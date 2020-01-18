#!/usr/bin/python

# Basename: mygit
# Version: 0.5.0
# VersionDate: 15 Aug 2019
# Description: A service control common Git business logic

# Example of usage::
# mygit push --debug --branch=Zoolander

# 					*** Actions ***
# branch: Name of branch to pull/push; completely arbitrary to admin
# 					*** Options ***
# pull: Auto-resolve merge conflicts using 'ours' strategy; favors existing changes
# push: Will create origin as needed; otherwise, it'll run a pull before push

from myboilerplate import ShellBoilerplate
import argparse

# ------------------------ Primary classes/functions ------------------------
# Both repository classes relinguish self to GitConfiguration

class RemoteRepository(object):
	def __init__(self, _super, _path):
		# if isinstance(_super, GitConfiguration):
		self.super = _super
		# self.super.log.debug("(RemoteRepository:__init__): Init")
		self.path = str(_path)


		if callable(self.Verify):
			self.exists = self.Verify()
		self:
			self.exists = False

		if self.exists:
			self.super.log.debug("Successfully found remote repository (origin) in good condition.")
		else:
			self.Create()


	def Verify(self):
		# self.super.log.debug("(RemoteRepository:Verify): Init")
		result = self.super.DirectoryExists(self.path)
		if result == False: return result

		command = "git rev-parse --is-bare-repository"
		rc, stdout, stderr = self.super.ProcessSync(command, self.path)
		result = (stdout == "true")
		return result



	def Create(self):
		self.super.log.debug("(RemoteRepository:Create): Init")
		self.super.log.warning("Remote repository (origin) not found; creating...")
		# Initialize the repository
		command = "git init --bare " + self.path
		rc, stdout, stderr = self.super.ProcessSync(command)
		if len(stdout) > 0: self.super.log.info(str(stdout))
		if len(stderr) > 0: self.super.log.error(str(stdout))
		failed = (rc != 0 and "Reinitialized existing Git repository" not in stdout)
		if failed: self.super.Fail()
		changed = (not failed and "skipped, since" not in stdout)

		if self.super.args.action == "push":
			# Temporary directory used to create origin/master branch on push
			self.tmpRepository = LocalRepository(self.super, "/tmp/delete_is_seen", self.path)
			# Ensure previous temporary directory is gone
			self.super.DeleteDirectory(self.tmpRepository.path)
			self.super.CreateDirectory(self.tmpRepository.path)
			# Cleanup temporary directory
			self.super.DeleteDirectory(self.tmpRepository.path)
			self.super.log.info("Successfully created remote repository!")
		else:
			self.super.log.error("Unable to locate remote repository.")
			self.super.Fail()


		def DeleteBranch(self):
			self.super.log.debug("(RemoteRepository:DeleteBranch): Init")
			# Delete branch from origin
			command = "git branch -D " + self.super.args.branch
			rc, stdout, stderr = self.super.ProcessSync(command, path)
			self.super.log.debug("(DeleteBranch): rc=" + str(rc))
			if len(stdout) > 0: self.super.log.info(str(stdout))
			if len(stderr) > 0: self.super.log.error(str(stderr))



class LocalRepository(object):
	def __init__(self, _super, _path, _remoteUrl):
		# if isinstance(_super, GitConfiguration):
		self.super = _super
		# self.super.log.debug("(LocalRepository:__init__): Init")
		self.path = str(_path)
		self.remoteUrl = str(_remoteUrl)

		if callable(self.Verify):
			self.exists = self.Verify()
		else:
			self.exists = False

		if not self.exists: self.Create()


	def Verify(self):
		# self.super.log.debug("(LocalRepository:Verify): Init")
		return self.super.DirectoryExists(self.path + "/.git")


	def Create(self):
		self.super.log.debug("(LocalRepository:Create): Init")
		# Initialize the repository
		command = "git init " + self.path
		rc, stdout, stderr = self.super.ProcessSync(command)
		if len(stdout) > 0: self.super.log.info(str(stdout))
		if len(stderr) > 0: self.super.log.error(str(stderr))
		failed = (rc != 0 and "Reinitialized existing Git repository" not in stdout)
		if failed: self.super.Fail()
		changed = (not failed and "skipped, since" not in stdout)

		if changed:
			# Create initial commit for origin/master
			# - pulls more reliable; helps prevent dangling HEAD refs
			# - while origin initializes with HEAD 'refs/heads/master'
			#   there's no actual 'master' branch until the first commit push
			command = "git commit --allow-empty -m 'Initial auto-commit'"
			rc, stdout, stderr = self.super.ProcessSync(command, self.path)
			# if len(stdout) > 0: self.super.log.info(str(stdout))
			# if len(stderr) > 0: self.super.log.error(str(stderr))
			# failed = (rc != 0 and "nothing to commit (working directory clean)" not in stdout)
			# if failed: self.super.Fail()
			# changed = (not failed and "nothing to commit (working directory clean)" not in stdout)

		self.RemoteLink()


	def RemoteLink(self):
		self.super.log.debug("(LocalRepository:RemoteLink): Init")

		# Check remote URL points to remote repository
		command = "git config --get remote.origin.url"
		rc, stdout, stderr = self.super.ProcessSync(command, self.path)
		if len(stdout) > 0: self.super.log.info(str(stdout))
		if len(stderr) > 0: self.super.log.error(str(stderr))

		if stdout == "":
			self.super.log.warning("Local repository is missing remote URL; adding...")
			# Adding remote URL
			command = "git remote add origin " + self.remoteUrl
			



# ------------------------ Main program ------------------------

if __name__ = '__main__':
	print("--------------------------------------------------------")
	print("DEBUG (__main__): Init")
