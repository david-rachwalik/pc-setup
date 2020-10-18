#!/usr/bin/env python

# Basename: azure
# Description: A service to control Azure resources
# Version: 0.1.1
# VersionDate: 15 Sep 2020

#       *** Resources ***
# account:          Will only pair with 'login'; sign-in/config for 'az' & 'az devops'
# secret:           Key vault secrets
# deploy:           Resource manager template deployment to resource group
# pipeline:         Pipelines (var groups, connections, end-points, etc.)
#       *** Actions ***
# login:            Ensure signed-in & configured; manual login prompt first time
# set:              Create/update an Azure resource
# get:              Show status output for a resource
# remove:           Delete resources (not immediately purge, based on retention)
#         *** Options ***
# --debug:          Enable to display log messages for development
# --quiet:          Enable to reduce verbosity; will error instead of login prompt

# :-Strategies-:    login_strategy, group_strategy, service_principal_strategy, secret_strategy


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

# --- Strategy  Commands ---

def resource_group_strategy(subscription, resource_group):
    if not _az.is_signed_in: return (False, False)
    if not (subscription and isinstance(subscription, str)): TypeError("resource_group_strategy() expects 'subscription' parameter as string")
    if not (resource_group and isinstance(resource_group, str)): TypeError("resource_group_strategy() expects 'resource_group' parameter as string")
    rg_changed = False

    # Ensure resource group exists

    return (True, rg_changed)


def key_vault_strategy(subscription, resource_group, key_vault):
    if not _az.is_signed_in: return (False, False)
    if not (subscription and isinstance(subscription, str)): TypeError("key_vault_strategy() expects 'subscription' parameter as string")
    if not (resource_group and isinstance(resource_group, str)): TypeError("key_vault_strategy() expects 'resource_group' parameter as string")
    if not (key_vault and isinstance(key_vault, str)): TypeError("key_vault_strategy() expects 'key_vault' parameter as string")
    kv_changed = False

    # Ensure key vault exists

    return (True, kv_changed)


def service_principal_strategy(subscription, resource_group, key_vault, sp_name, sp_dir):
    if not (subscription and isinstance(subscription, str)): TypeError("service_principal_strategy() expects 'subscription' parameter as string")
    if not (sp_name and isinstance(sp_name, str)): TypeError("service_principal_strategy() expects 'sp_name' parameter as string")
    if not (sp_dir and isinstance(sp_dir, str)): TypeError("service_principal_strategy() expects 'sp_dir' parameter as string")
    sp_changed = False
    service_principal = None
    kv_secret_value = ""
    # Full filepath to service principal data
    sp_name = az.format_resource(sp_name)
    sp_path = sh.path_join(sh.path_expand(sp_dir), "{0}.json".format(sp_name))

    # Ensure service principal exists in Azure and local
    if sh.path_exists(sp_path, "f"):
        # Gather login info from service principal JSON
        _log.debug("service principal file found, gathering credentials...")
        service_principal = az.service_principal_get(sp_name, sp_dir)
    else:
        _log.debug("service principal file missing, checking Azure...")
        if not _az.is_signed_in: return (False, False)

        # Ensure key vault and service principal exists
        service_principal = az.service_principal_get(sp_name)
        (kv_succeeded, kv_changed) = key_vault_strategy(subscription, resource_group, key_vault)
        if service_principal and kv_succeeded:
            # Check for passphrase as key vault secret (to share across systems)
            kv_secret_value = az.key_vault_secret_get(key_vault, sp_name)
            # _log.debug("kv_secret_value: {0}".format(kv_secret_value))
            if kv_secret_value:
                _log.debug("service principal password found in key vault, saving credentials...")
                service_principal.password = kv_secret_value
            else:
                # Service principal in Azure but not local file, must reset pass to regain access
                _log.debug("service principal successfully found, resetting credentials...")
                service_principal = az.service_principal_rbac_set(key_vault, sp_name, True)
        else:
            _log.debug("service principal credentials not found, creating...")
            service_principal = az.service_principal_rbac_set(key_vault, sp_name)

        # Last chance to have service principal
        # if not service_principal:    
        #     _log.error("failed to retrieve service principal, exiting...")
        #     sh.process_fail()

        # if not service_principal:
        #     _log.error("failed to retrieve service principal, likely due to insufficient privileges on account, signing out...")
        #     az.account_logout()
        #     # Calling 'az login' in script works but the prompt in subprocess causes display issues
        #     _log.error("not signed-in, enter 'az login' to manually login before repeating your previous command")
        #     sh.process_fail()

        # Last chance to have service principal
        if not service_principal: return (False, False)

        # Store password/credentials in JSON file
        az.service_principal_save(sp_path, service_principal)
        if not kv_secret_value:
            # Store password/credentials in key vault
            az.key_vault_secret_set(key_vault, sp_name, service_principal.password)

        # TODO: manage service principal security groups
        # use 'az role assignment create' on groups, not service principals
        # https://docs.microsoft.com/en-us/cli/azure/create-an-azure-service-principal-azure-cli#manage-service-principal-roles
        
        # TODO: manage service principal security access to key vaults

        sp_changed = True

    return (service_principal, sp_changed)


def login_strategy(organization, subscription, resource_group, key_vault, sp_name, sp_dir, retry=True):
    global _az
    if not (organization and isinstance(organization, str)): TypeError("'organization' parameter expected as string")
    if not (subscription and isinstance(subscription, str)): TypeError("login_strategy() expects 'subscription' parameter as string")
    if not (sp_name and isinstance(sp_name, str)): TypeError("login_strategy() expects 'sp_name' parameter as string")
    if not (sp_dir and isinstance(sp_dir, str)): TypeError("login_strategy() expects 'sp_dir' parameter as string")
    # Full filepath to service principal data
    sp_name = az.format_resource(sp_name)
    sp_path = sh.path_join(sh.path_expand(sp_dir), "{0}.json".format(sp_name))
    # Check if account subscription exists
    _log.info("checking if already signed-in...")
    # First chance to be signed-in
    _az = az.account_get(subscription)

    # Ensure service principal credentials exist
    (service_principal, sp_changed) = service_principal_strategy(subscription, resource_group, key_vault, sp_name, sp_dir)
    if _az.is_signed_in and not service_principal:
        _log.error("failed to retrieve service principal, likely due to insufficient privileges on account, signing out...")
        az.account_logout()
        _az.is_signed_in = False
        # Prompt manual 'az login' indirectly
        _az = login_strategy(organization, subscription, resource_group, key_vault, sp_name, sp_dir)

    if not _az.is_signed_in:
        if service_principal:
            # Attempt login with service principal credentials found, last chance to be signed-in
            _az = az.account_login(organization, service_principal.name, service_principal.password)
            if not _az.is_signed_in:
                if retry:
                    # Will retry recursively only once
                    _log.warning("Azure login with service principal failed, saving backup and retrying...")
                    sh.file_backup(sp_path)
                    _az = login_strategy(organization, subscription, resource_group, key_vault, sp_name, sp_dir, False)
                else:
                    _log.error("Azure login with service principal failed again, exiting...")
                    sh.process_fail()
        else:
            # Calling 'az login' in script works but the prompt in subprocess causes display issues
            _log.error("not signed-in, enter 'az login' to manually login before repeating your previous command")
            sh.process_fail()

    # elif used to limit recursive activity
    if sp_changed:
        # Confirm updated service principal login connects
        _log.debug("attempting login with service principal...")
        az.account_logout()
        _az.is_signed_in = False
        _az = login_strategy(organization, subscription, resource_group, key_vault, sp_name, sp_dir)
        # No need to rename/backup SP credentials here if failed - it'll occur recursively
    elif not _az.subscription_is_default:
        # Ensure subscription is currently active
        _log.debug("activating the selected subscription...")
        account_active = az.account_set(subscription)
        if not account_active:
            _log.error("failed to activate subscription")
            sh.process_fail()

    _log.info("successfully signed into Azure!")
    return _az



# --- Subscription Commands ---

def login():
    # az.login_strategy(args.subscription, args.cert_path, args.tenant, args.key_vault)
    # _log.debug("1st random password: {0}".format(az.get_random_password()))
    # _log.debug("2nd random password: {0}".format(az.get_random_password()))
    # _log.debug("3rd random password: {0}".format(az.get_random_password()))

    # az.login_strategy(args.organization, args.subscription, args.login_resource_group, args.login_key_vault, args.login_service_principal, args.login_service_principal_dir)
    login_strategy(args.organization, args.subscription, args.login_resource_group, args.login_key_vault, args.login_service_principal, args.login_service_principal_dir)


# --- Deploy Commands ---

def app_create():
    _log.debug("<mock 'app_create' group>")
    # Register application object in Azure AD
    # Create new ASP.NET Core web app
    
    login()

    rg_good = az.resource_group_set(args.resource_group, args.location)
    if not rg_good:
        _log.error("failed to create resource group")
        sh.process_fail()
    # Create a hardened container (a vault) in Azure
    az.key_vault_set(args.key_vault, args.resource_group)
    # Add a [key, secret, certificate] to the key vault
    az.key_vault_secret_set(args.key_vault, args.secret_key, args.secret_value)
    # Register an application with Azure Active Directory (AD)
    # Authorize an application to use a key or secret
    # Set key vault advanced access policies
    # Work with Hardware security modules (HSMs)
    # Delete the key vault and associated keys and secrets
    # Miscellaneous Azure Cross-Platform Command-line Interface Commands


def secret():
    login()

    _log.debug("<mock 'secret' group>")
    # Create resource group, key vault, key vault secret
    rg_good = az.resource_group_set(args.resource_group, args.location)
    if not rg_good:
        _log.error("failed to create resource group")
        sh.process_fail()
    # Create a hardened container (a vault) in Azure
    az.key_vault_set(args.key_vault, args.resource_group)
    # Add a [key, secret, certificate] to the key vault
    az.key_vault_secret_set(args.key_vault, args.secret_key, args.secret_value)
    # Set key vault advanced access policies


def deploy():
    _log.debug("<mock 'deploy' group>")
    # Deploy ARM templates:
    # - resource group, app service plan, web app service
    # - resource group, app service plan, web app service, sql server, sql database, connection


def pipeline():
    _log.debug("<mock 'pipeline' group>")
    # Create pipeline for project
    # - build csproj, deploy Python (pip) packages
    # - build csproj, deploy NuGet packages
    # - build csproj, deploy ARM templates
    # - build csproj, deploy .zip file to web app service
    # - build csproj, deploy .sql file to sql database



# ------------------------ Main program ------------------------

# Initialize the logger
basename = "azure"
args = LogArgs() # for external modules
# log_file = "/var/log/{0}.log".format(basename)
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

        # --- Global defaults ---
        parser.add_argument("action", default="get", const="get", nargs="?", choices=["get", "set", "remove"])
        parser.add_argument("--debug", action="store_true")
        parser.add_argument("--log-path", default="")
        # --- Account defaults ---
        parser.add_argument("--organization", "-o", default="davidrachwalikoutlook")
        parser.add_argument("--subscription", "-s", default="Pay-As-You-Go")
        # parser.add_argument("--cert-path", default="~/.local/az_cert.pem")
        # ~/.local/az_service_principals/{service-principal}.json
        service_principal_dir = "~/.local/az_service_principals"
        parser.add_argument("--service-principal-dir", "-d", default=service_principal_dir)
        parser.add_argument("--service-principal", "-p", default="")
        # --- Login defaults ---
        parser.add_argument("--login-service-principal-dir", "-D", default=service_principal_dir)
        parser.add_argument("--login-service-principal", "-P", default="main-rbac-sp")
        parser.add_argument("--login-resource-group", "-G", default="Main")
        parser.add_argument("--login-key-vault", "-V", default="main-keyvault")
        # --- Resource defaults ---
        # parser.add_argument("--environment", "-e", default="Dev")
        parser.add_argument("--location", "-l", default="southcentralus") # az account list-locations
        parser.add_argument("--resource-group", "-g", default="")
        parser.add_argument("--key-vault", "-v", default="")
        parser.add_argument("--secret-key")
        parser.add_argument("--secret-value")
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
        # Configure the azure_boilerplate logger
        _az_log = get_logger("azure_boilerplate")
        set_handlers(_az_log, log_handlers)
        az.args.debug = args.debug


    # ------------------------ Business Logic (group/action) ------------------------

    _log.debug("args: {0}".format(args))
    # _log.debug("'{0}' group detected".format(args.group))
    # _log.debug("'{0}' action detected".format(args.action))
    _log.debug("--------------------------------------------------------")
    _az = az.Account()

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
