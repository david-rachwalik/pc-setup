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
# subscription:     Will only pair with 'login'; sign-in/config for 'az' & 'az devops'
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
    logger.debug("(login): Init")
    logger.debug("(login): prompt: {0}".format(not args.quiet))
    az.subscription_login(not args.quiet)


def secret():
    logger.debug("(secret): Init")
    logger.debug("(secret): <mock 'secret' group>")


def deploy():
    logger.debug("(deploy): Init")
    logger.debug("(deploy): <mock 'deploy' group>")


def pipeline():
    logger.debug("(pipeline): Init")
    logger.debug("(pipeline): <mock 'pipeline' group>")



# ------------------------ Main program ------------------------

# Initialize the logger
basename = "azure"
log_file = "/var/log/{0}.log".format(basename)
log_options = LogOptions(basename)
logger = get_logger(log_options)

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
        parser.add_argument("--key")
        parser.add_argument("--value")
        return parser.parse_args()
    args = parse_arguments()

    # Configure the main logger
    log_level = 20                  # logging.INFO
    if args.debug: log_level = 10   # logging.DEBUG
    logger.setLevel(log_level)

    # Configure the shell_boilerplate logger
    if args.debug:
        sh_logger = get_logger("shell_boilerplate")
        sh_logger.setLevel(log_level)

    # Configure the azure_boilerplate logger
    if args.debug:
        az_logger = get_logger("azure_boilerplate")
        az_logger.setLevel(log_level)


    # ------------------------ Business Logic (group/action) ------------------------

    logger.debug("args: {0}".format(args))
    # logger.debug("'{0}' group detected".format(args.group))
    # logger.debug("'{0}' action detected".format(args.action))
    logger.debug("--------------------------------------------------------")

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
    logger.debug("--------------------------------------------------------")
    logger.debug("--- end point reached :3 ---")
    sh.process_exit()

    # :: Usage Example ::
    # setup --tags "py" --skip-tags "windows"
    # azure --debug login
