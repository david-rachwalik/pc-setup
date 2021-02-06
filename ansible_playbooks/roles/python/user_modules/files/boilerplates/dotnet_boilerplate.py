#!/usr/bin/env python

# Basename: dotnet_boilerplate
# Description: Common business logic for ASP.NET Core
# Version: 0.1.0
# VersionDate: 12 Nov 2020
# https://docs.microsoft.com/en-us/ef/core/miscellaneous/cli/dotnet

# --- Global Methods ---
# solution:                     solution_new, solution_project_list, solution_project_add
# project:                      project_new, project_package_list, project_package_add
# identity:                     project_identity_scaffold

from logging_boilerplate import *
import shell_boilerplate as sh
# import json, time

try:
    # Python 2 has both 'str' (bytes) and 'unicode' text
    basestring = basestring
    unicode = unicode
except NameError:
    # Python 3 names the unicode data type 'str'
    basestring = str
    unicode = str

# ------------------------ Global Methods ------------------------

# --- Solution Commands ---

# https://docs.microsoft.com/en-us/dotnet/core/tools/dotnet-new
def solution_new(dotnet_dir, application):
    if not (dotnet_dir and isinstance(dotnet_dir, str)): TypeError("'dotnet_dir' parameter expected as string")
    if not (application and isinstance(application, str)): TypeError("'application' parameter expected as string")
    template = "sln"
    app_dir = sh.path_join(dotnet_dir, application)
    command = ["dotnet", "new", template, "--output={0}".format(app_dir), "--name={0}".format(application)]
    # command.append("--dry-run")
    sh.print_command(command)
    (stdout, stderr, rc) = sh.subprocess_run(command)
    # sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
    return bool(rc == 0)


# https://docs.microsoft.com/en-us/dotnet/core/tools/dotnet-sln
def solution_project_add(dotnet_dir, application, project):
    if not (dotnet_dir and isinstance(dotnet_dir, str)): TypeError("'dotnet_dir' parameter expected as string")
    if not (application and isinstance(application, str)): TypeError("'application' parameter expected as string")
    if not (project and isinstance(project, str)): TypeError("'project' parameter expected as string")
    # solution_dir = sh.path_join(dotnet_dir, application)
    app_sln = sh.path_join(dotnet_dir, application, "{0}.sln".format(application))
    # project_dir = sh.path_join(dotnet_dir, application, project)
    app_csproj = sh.path_join(dotnet_dir, application, project, "{0}.csproj".format(project))

    command = ["dotnet", "sln", app_sln, "add", app_csproj]
    sh.print_command(command)
    (stdout, stderr, rc) = sh.subprocess_run(command)
    # sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
    return bool(rc == 0)



# --- Project Commands ---

# 'dotnet new' automatically calls build and restore
# https://docs.microsoft.com/en-us/dotnet/core/tools/dotnet-new
def project_new(dotnet_dir, application, project, strat, framework="net5.0"):
    client_id = ""
    if not (dotnet_dir and isinstance(dotnet_dir, str)): TypeError("'dotnet_dir' parameter expected as string")
    if not (application and isinstance(application, str)): TypeError("'application' parameter expected as string")
    if not (project and isinstance(project, str)): TypeError("'project' parameter expected as string")
    if not (strat and isinstance(strat, str)): TypeError("'strat' parameter expected as string")
    template = "webapp"
    domain = "https://localhost:5001"
    project_dir = sh.path_join(dotnet_dir, application, project)

    command = ["dotnet", "new", template]
    command.append("--framework={0}".format(framework))
    command.append("--output={0}".format(project_dir))
    if strat == "identity":
        command.append("--auth={0}".format("MultiOrg"))
        command.append("--client-id={0}".format(client_id))
    else:
        # command.append("--auth={0}".format("None"))
        command.append("--domain={0}".format(domain))
    command.append("--org-read-access")

    sh.print_command(command)
    (stdout, stderr, rc) = sh.subprocess_run(command)
    # sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
    # _log.debug("Successfully created ASP.NET Core project")
    return bool(rc == 0)


# Currently difficult to parse - will eventually have --json option: https://github.com/NuGet/Home/issues/7752
# - TODO: skip attempting to add packages each run when this change occurs
def project_package_list(dotnet_dir, application, project):
    if not (dotnet_dir and isinstance(dotnet_dir, str)): TypeError("'dotnet_dir' parameter expected as string")
    if not (application and isinstance(application, str)): TypeError("'application' parameter expected as string")
    if not (project and isinstance(project, str)): TypeError("'project' parameter expected as string")
    results = []
    project_dir = sh.path_join(dotnet_dir, application, project)
    command = ["dotnet", "list", project_dir, "package"]
    sh.print_command(command)
    (stdout, stderr, rc) = sh.subprocess_run(command)
    # sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
    # Parse project package list
    if (rc == 0 and stdout):
        stdout_lines = stdout.splitlines()
        for line in stdout_lines:
            line_edit = line.lstrip()
            if line_edit.startswith("> "):
                line_edit_list = line_edit.split()
                results.append(line_edit_list[1])
    # _log.debug("results: {0}".format(results))
    results.sort()
    return results


# https://docs.microsoft.com/en-us/dotnet/core/tools/dotnet-add
def project_package_add(dotnet_dir, application, project, package):
    if not (dotnet_dir and isinstance(dotnet_dir, str)): TypeError("'dotnet_dir' parameter expected as string")
    if not (application and isinstance(application, str)): TypeError("'application' parameter expected as string")
    if not (project and isinstance(project, str)): TypeError("'project' parameter expected as string")
    if not (package and isinstance(package, str)): TypeError("'package' parameter expected as string")
    project_dir = sh.path_join(dotnet_dir, application, project)
    command = ["dotnet", "add", project_dir, "package", package]
    sh.print_command(command)
    (stdout, stderr, rc) = sh.subprocess_run(command)
    # sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
    return bool(rc == 0)



# --- Scaffold Commands ---

# https://docs.microsoft.com/en-us/aspnet/core/fundamentals/tools/dotnet-aspnet-codegenerator
def project_identity_scaffold(project_dir):
    if not (project_dir and isinstance(project_dir, str)): TypeError("'project_dir' parameter expected as string")
    command = ["dotnet", "aspnet-codegenerator", "identity", "--useDefaultUI",
        "--project={0}".format(project_dir)
    ]
    sh.print_command(command)
    (stdout, stderr, rc) = sh.subprocess_run(command)
    sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
    return bool(rc == 0)



# ------------------------ Main Program ------------------------

# Initialize the logger
basename = "dotnet_boilerplate"
args = LogArgs() # for external modules
log_options = LogOptions(basename)
_log = get_logger(log_options)

if __name__ == "__main__":
    # Returns argparse.Namespace; to pass into function, use **vars(self.args)
    def parse_arguments():
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--debug", action="store_true")
        parser.add_argument("--log-path", default="")
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
    # python ~/.local/lib/python3.6/site-packages/dotnet_boilerplate.py --debug
