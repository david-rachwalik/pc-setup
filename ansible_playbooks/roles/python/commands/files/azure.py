#!/usr/bin/env python

# Basename: azure
# Description: A service to control Azure resources
# Version: 0.1.1
# VersionDate: 15 Sep 2020

#       *** Actions ***
# login:            Ensure signed-in & configured; manual login prompt first time
# set:              Create/update an Azure resource
# get:              Show status output for a resource
# remove:           Delete resources (not immediately purge, based on retention)
#       *** Resources ***
# account:          Will only pair with 'login'; sign-in/config for 'az' & 'az devops'
# secret:           Key vault secrets
# deploy:           Resource manager template deployment to resource group
# pipeline:         Pipelines (var groups, connections, end-points, etc.)
#         *** Options ***
# --debug:          Enable to display log messages for development
# --quiet:          Enable to reduce verbosity; will error instead of login prompt



#         *** Actions ***
# login:            Ensure credential file exists or prompts manual login to create
# show:             Print output for a resource, key vault secret, etc.
# register:         Register an Azure Active Directory application
# deploy:           Deploy an application to Azure (webapp, api, nuget package)
# status:           View running state of deployed application

from logging_boilerplate import *
import shell_boilerplate as sh
import azure_boilerplate as az

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

def login():
    _log.debug("(login): Init")
    _log.debug("(login): prompt: {0}".format(not args.quiet))
    az.account_login(not args.quiet)



# --- Deploy Commands ---

def app_create():
    _log.debug("(app_create): Init")
    _log.debug("(app_create): <mock 'app_create' group>")
    # Register application object in Azure AD
    # Create new ASP.NET Core web app


def secret():
    _log.debug("(secret): Init")
    _log.debug("(secret): <mock 'secret' group>")
    # Create resource group, key vault, key vault secret

    login()

    # Create a hardened container (a vault) in Azure
    az.key_vault_create()
    # Add a [key, secret, certificate] to the key vault
    # Register an application with Azure Active Directory (AD)
    # Authorize an application to use a key or secret
    # Set key vault advanced access policies
    # Work with Hardware security modules (HSMs)
    # Delete the key vault and associated keys and secrets
    # Miscellaneous Azure Cross-Platform Command-line Interface Commands


def deploy():
    _log.debug("(deploy): Init")
    _log.debug("(deploy): <mock 'deploy' group>")
    # Deploy ARM templates:
    # - resource group, app service plan, web app service
    # - resource group, app service plan, web app service, sql server, sql database, connection


def pipeline():
    _log.debug("(pipeline): Init")
    _log.debug("(pipeline): <mock 'pipeline' group>")
    # Create pipeline for project
    # - build csproj, deploy Python (pip) packages
    # - build csproj, deploy NuGet packages
    # - build csproj, deploy ARM templates
    # - build csproj, deploy .zip file to web app service
    # - build csproj, deploy .sql file to sql database



# ------------------------ Main program ------------------------

# Initialize the logger
basename = "azure"
log_file = "/var/log/{0}.log".format(basename)
log_options = LogOptions(basename)
_log = get_logger(log_options)

if __name__ == "__main__":
    # When 'default' doesn't work, add nargs="?" and const=(same value as default)
    def parse_arguments():
        import argparse
        parser = argparse.ArgumentParser()
        # Use Subcommands
        subparser = parser.add_subparsers(dest="group")

        # Create parser for 'login' command
        parser_login = subparser.add_parser("login")
        # parser_login.set_defaults(func=login)

        # Create parser for 'secret' command
        parser_secret = subparser.add_parser("secret")
        # parser_secret.set_defaults(func=secret)

        # Create parser for 'deploy' command
        parser_deploy = subparser.add_parser("deploy")
        # parser_deploy.set_defaults(func=deploy)

        # Create parser for 'pipeline' command
        parser_pipeline = subparser.add_parser("pipeline")
        # parser_pipeline.set_defaults(func=pipeline)

        # Global defaults
        parser.add_argument("action", default="get", const="get", nargs="?", choices=["get", "set", "remove"])
        parser.add_argument("--debug", "-d", action="store_true")
        parser.add_argument("--quiet", "-q", action="store_true")
        # Resource defaults
        parser.add_argument("--resource-group", "-g", default="Main")
        parser.add_argument("--key-vault", "-v", default="main-keyvault")
        parser.add_argument("--secret-key")
        parser.add_argument("--secret-value")
        return parser.parse_args()
    args = parse_arguments()

    # Configure the main logger
    log_level = 20                  # logging.INFO
    if args.debug: log_level = 10   # logging.DEBUG
    log_stream_options = LogHandlerOptions(log_level)
    set_handlers(_log, [log_stream_options])

    # Configure the shell_boilerplate logger
    if args.debug:
        sh_log_options = LogOptions("shell_boilerplate", log_level)
        sh_log = get_logger(sh_log_options)
        set_handlers(sh_log, [log_stream_options])

    # Configure the azure_boilerplate logger
    if args.debug:
        az_log_options = LogOptions("azure_boilerplate", log_level)
        az_log = get_logger(az_log_options)
        set_handlers(az_log, [log_stream_options])


    # ------------------------ Business Logic (group/action) ------------------------

    _log.debug("args: {0}".format(args))
    # _log.debug("'{0}' group detected".format(args.group))
    # _log.debug("'{0}' action detected".format(args.action))
    _log.debug("--------------------------------------------------------")

    # --- Run Actions ---

    if args.group == "login":
        login()
    
    elif args.group == "secret":
        secret()
    
    elif args.group == "deploy":
        deploy()
    
    elif args.group == "pipeline":
        pipeline()


    # If we get to this point, assume all went well
    _log.debug("--------------------------------------------------------")
    _log.debug("--- end point reached :3 ---")
    sh.process_exit()

    # :: Usage Example ::
    # setup --tags "py" --skip-tags "windows"
    # azure --debug login
    # azure --debug --secret-key="AutoTestKey" --secret-value="007" secret
