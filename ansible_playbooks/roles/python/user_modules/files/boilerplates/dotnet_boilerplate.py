#!/usr/bin/env python

# Basename: dotnet_boilerplate
# Description: Common business logic for ASP.NET Core
# Version: 0.1.0
# VersionDate: 12 Nov 2020
# https://docs.microsoft.com/en-us/ef/core/miscellaneous/cli/dotnet

# --- Global Methods ---
# solution:                     solution_new, solution_project_list, solution_project_add
# project:                      project_new, project_package_list, project_package_add

from logging_boilerplate import *
import shell_boilerplate as sh
import json, time, re

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
    sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
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
    sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
    return bool(rc == 0)



# --- Project Commands ---

# 'dotnet new' automatically calls build and restore
# https://docs.microsoft.com/en-us/dotnet/core/tools/dotnet-new
def project_new(dotnet_dir, application, project, strat):
    client_id = ""
    if not (dotnet_dir and isinstance(dotnet_dir, str)): TypeError("'dotnet_dir' parameter expected as string")
    if not (application and isinstance(application, str)): TypeError("'application' parameter expected as string")
    if not (project and isinstance(project, str)): TypeError("'project' parameter expected as string")
    if not (strat and isinstance(strat, str)): TypeError("'strat' parameter expected as string")
    template = "webapp"
    framework = "netcoreapp3.1"
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
    sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)

    # if (rc != 0): return Account()
    # # Return the parsed account data
    # results = Account(stdout)
    # # _log.debug("results: {0}".format(results))
    # _log.debug("Successfully created ASP.NET Core project")
    # return results
    return bool(rc == 0)


# Currently difficult to parse - will eventually have --json option: https://github.com/NuGet/Home/issues/7752
# - TODO: skip attempting to add packages each run when this change occurs
def project_package_list(dotnet_dir, application, project):
    if not (dotnet_dir and isinstance(dotnet_dir, str)): TypeError("'dotnet_dir' parameter expected as string")
    if not (application and isinstance(application, str)): TypeError("'application' parameter expected as string")
    if not (project and isinstance(project, str)): TypeError("'project' parameter expected as string")
    project_dir = sh.path_join(dotnet_dir, application, project)

    command = ["dotnet", "list", project_dir, "package"]
    sh.print_command(command)
    (stdout, stderr, rc) = sh.subprocess_run(command)
    sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
    results = stdout
    # _log.debug("results: {0}".format(results))
    return results


def project_package_add(dotnet_dir, application, project, package):
    if not (dotnet_dir and isinstance(dotnet_dir, str)): TypeError("'dotnet_dir' parameter expected as string")
    if not (application and isinstance(application, str)): TypeError("'application' parameter expected as string")
    if not (project and isinstance(project, str)): TypeError("'project' parameter expected as string")
    if not (package and isinstance(package, str)): TypeError("'package' parameter expected as string")
    project_dir = sh.path_join(dotnet_dir, application, project)

    command = ["dotnet", "add", project_dir, "package", package]

    sh.print_command(command)
    (stdout, stderr, rc) = sh.subprocess_run(command)
    sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
    return bool(rc == 0)


def project_package_set(template, dotnet_dir, application, project, strat):
    if not (template and isinstance(template, str)): TypeError("'template' parameter expected as string")
    auth = "None"
    # --- .NET NuGet Packages (https://www.nuget.org/packages/*) ---
    # Development Packages
    dotnet_packages = [
        "Microsoft.VisualStudio.Web.BrowserLink",
        "Microsoft.CodeAnalysis.FxCopAnalyzers"
    ]
    if strat == "database":
        dotnet_packages.append([
            # Database provider automatically includes Microsoft.EntityFrameworkCore
            "Microsoft.EntityFrameworkCore.SqlServer", # Install SQL Server database provider
            "Microsoft.EntityFrameworkCore.Design", # Install EF Core design package
            "Microsoft.EntityFrameworkCore.Tools",
            "Microsoft.VisualStudio.Web.CodeGeneration.Design",
            "Microsoft.Extensions.Logging.Debug",
            "NSwag.AspNetCore" # Swagger / OpenAPI
        ])
    if strat == "identity":
        dotnet_packages.append([
            "Microsoft.AspNetCore.Authentication.AzureAD.UI"
            # "Install-Package Microsoft.Owin.Security.OpenIdConnect",
            # "Install-Package Microsoft.Owin.Security.Cookies",
            # "Install-Package Microsoft.Owin.Host.SystemWeb"
        ])

    
    # https://docs.microsoft.com/en-us/dotnet/core/tools/dotnet-add
    # https://docs.ansible.com/ansible/latest/modules/command_module.html
    # https://docs.microsoft.com/en-us/ef/core/miscellaneous/cli/dotnet
    _log.debug("installing packages to ASP.NET Core project")
    for package in dotnet_packages:
        project_package_add(package)
        if not package_succeeded:
            _log.error("failed to add package: {0}".format(package))
            sh.process_fail()


    # dotnet_database_tools:
    # # https://docs.microsoft.com/en-us/aspnet/core/data/ef-rp
    # - dotnet-ef                                 # Install Entity Framework Core
    # # https://docs.microsoft.com/en-us/aspnet/core/security/authentication/scaffold-identity
    # - dotnet-aspnet-codegenerator               # Install Code Generator (Scaffold)

    # # https://www.nuget.org/packages/*
    # dotnet_development_packages:
    # - Microsoft.VisualStudio.Web.BrowserLink
    # - Microsoft.CodeAnalysis.FxCopAnalyzers

    # # https://docs.microsoft.com/en-us/aspnet/core/data/ef-rp/intro#scaffold-student-pages
    # # The Microsoft.VisualStudio.Web.CodeGeneration.Design package is required for scaffolding.
    # # Although the app won't use SQL Server, the scaffolding tool needs the SQL Server package.
    # dotnet_database_packages:
    # # Automatically includes Microsoft.EntityFrameworkCore as dependency
    # # - Microsoft.EntityFrameworkCore.Sqlite      # Install SQLite database provider
    # - Microsoft.EntityFrameworkCore.SqlServer   # Install SQL Server database provider
    # - Microsoft.EntityFrameworkCore.Design      # Install EF Core design package
    # - Microsoft.EntityFrameworkCore.Tools
    # - Microsoft.VisualStudio.Web.CodeGeneration.Design
    # - Microsoft.Extensions.Logging.Debug
    # - NSwag.AspNetCore                          # Swagger / OpenAPI

    # dotnet_identity_packages:
    # - Microsoft.AspNetCore.Authentication.AzureAD.UI
    # # Install-Package Microsoft.Owin.Security.OpenIdConnect
    # # Install-Package Microsoft.Owin.Security.Cookies
    # # Install-Package Microsoft.Owin.Host.SystemWeb


    sh.print_command(command)
    (stdout, stderr, rc) = sh.subprocess_run(command)
    # sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
    if (rc != 0): return Account()
    # Return the parsed account data
    results = Account(stdout)
    # _log.debug("results: {0}".format(results))
    _log.debug("Successfully created ASP.NET Core project")
    return results



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
