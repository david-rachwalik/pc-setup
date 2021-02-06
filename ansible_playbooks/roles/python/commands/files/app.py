#!/usr/bin/env python

# Basename: app
# Description: A service to control application resources (Azure, ASP.NET Core)
# Version: 0.2.0
# VersionDate: 4 Nov 2020

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
import dotnet_boilerplate as net
import git_boilerplate as git

try:
    # Python 2 has both 'str' (bytes) and 'unicode' text
    basestring = basestring
    unicode = unicode
except NameError:
    # Python 3 names the unicode data type 'str'
    basestring = str
    unicode = str

# ------------------------ Global Azure Commands ------------------------

# --- Strategies ---

def resource_group_strategy(subscription, rg_name, location):
    if not _az.is_signed_in: return (False, False)
    if not (subscription and isinstance(subscription, str)): TypeError("resource_group_strategy() expects 'subscription' parameter as string")
    if not (rg_name and isinstance(rg_name, str)): TypeError("resource_group_strategy() expects 'rg_name' parameter as string")
    rg_changed = False

    # Ensure resource group exists
    resource_group = resource_group_get(rg_name)

    if not resource_group:
        _log.warning("resource group is missing, creating...")
        resource_group = _az.resource_group_set(rg_name, location)
        rg_changed = True

    return (resource_group, rg_changed)


def key_vault_strategy(subscription, resource_group, key_vault):
    if not _az.is_signed_in: return (False, False)
    if not (subscription and isinstance(subscription, str)): TypeError("key_vault_strategy() expects 'subscription' parameter as string")
    if not (resource_group and isinstance(resource_group, str)): TypeError("key_vault_strategy() expects 'resource_group' parameter as string")
    if not (key_vault and isinstance(key_vault, str)): TypeError("key_vault_strategy() expects 'key_vault' parameter as string")
    kv_changed = False

    # Ensure key vault exists
    
    # key_vault = az.key_vault_list(resource_group, key_vault)

    return (True, kv_changed)


def ad_group_strategy(subscription, member_id, group_name="main-ad-group"):
    if not _az.is_signed_in: return (False, False)
    if not (subscription and isinstance(subscription, str)): TypeError("'subscription' parameter expected as string")
    if not (member_id and isinstance(member_id, str)): TypeError("'member_id' parameter expected as string")
    if not (group_name and isinstance(group_name, str)): TypeError("'group_name' parameter expected as string")

    # Ensure active directory group exists
    ad_group = az.ad_group_get(group_name)
    group_changed = False
    if not ad_group.is_valid:
        _log.warning("active directory group is missing, creating...")
        (ad_group, group_changed) = az.ad_group_set(group_name)

    # Ensure active directory group member exists
    ad_group_member_exists = az.ad_group_member_get(group_name, member_id)
    if not ad_group_member_exists:
        _log.warning("active directory group member is missing, adding...")
        ad_group_member_exists = az.ad_group_member_set(group_name, member_id)

    # Ensure role is assigned to active directory group
    scope = "/subscriptions/{0}".format(_az.subscription_id)
    role_assigned = az.role_assign_get(ad_group.id, scope)
    if not role_assigned:
        _log.warning("role is not assigned to active directory group, adding...")
        role_assigned = az.role_assign_set(ad_group.id, scope)

    return (ad_group, group_changed)


def service_principal_strategy(tenant, sp_name, app_id):
    if not (tenant and isinstance(tenant, str)): TypeError("'tenant' parameter expected as string")
    if not (sp_name and isinstance(sp_name, str)): TypeError("'sp_name' parameter expected as string")
    sp_changed = False
    service_principal = None
    kv_secret_value = ""
    # Full filepath to service principal data
    sp_name = sh.format_resource(sp_name)
    # Ensure service principal exists
    service_principal = az.service_principal_get(sp_name, tenant=tenant)
    if not service_principal.appId:
        _log.debug("service principal credentials not found, creating...")
        service_principal = az.service_principal_set(sp_name, app_id)
        sp_changed = True
    return (service_principal, sp_changed)


def login_service_principal_strategy(subscription, resource_group, key_vault, sp_name, sp_dir):
    if not (subscription and isinstance(subscription, str)): TypeError("'subscription' parameter expected as string")
    if not (resource_group and isinstance(resource_group, str)): TypeError("'resource_group' parameter expected as string")
    if not (key_vault and isinstance(key_vault, str)): TypeError("'key_vault' parameter expected as string")
    if not (sp_name and isinstance(sp_name, str)): TypeError("'sp_name' parameter expected as string")
    if not (sp_dir and isinstance(sp_dir, str)): TypeError("'sp_dir' parameter expected as string")
    sp_changed = False
    service_principal = None
    kv_secret_value = ""
    # Full filepath to service principal data
    sp_name = sh.format_resource(sp_name)
    sp_path = sh.path_join(sh.path_expand(sp_dir), "{0}.json".format(sp_name))

    # Ensure service principal exists in Azure and local
    if sh.path_exists(sp_path, "f"):
        # Gather login info from service principal JSON
        _log.debug("service principal file exists, checking file...")
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
        if not service_principal: return (False, False)

        # Store password/credentials in JSON file
        az.service_principal_save(sp_path, service_principal)
        if not kv_secret_value:
            # Store password/credentials in key vault
            az.key_vault_secret_set(key_vault, sp_name, service_principal.password)

        # TODO: manage service principal security groups
        # use 'az role assignment create' on groups, not service principals
        # https://docs.microsoft.com/en-us/cli/azure/create-an-azure-service-principal-azure-cli#manage-service-principal-roles
        
        # TODO: manage service principal security access to Key Vault:
        # - manually enabled ARM for template deployment in Portal
        # - manually added the service principal as access policy in Portal
        # - examine key_vault returned from strategy

        sp_changed = True

    return (service_principal, sp_changed)


def login_strategy(tenant, subscription, resource_group, key_vault, sp_name, sp_dir, retry=True):
    global _az
    if not (tenant and isinstance(tenant, str)): TypeError("'tenant' parameter expected as string")
    if not (subscription and isinstance(subscription, str)): TypeError("'subscription' parameter expected as string")
    if not (sp_name and isinstance(sp_name, str)): TypeError("'sp_name' parameter expected as string")
    if not (sp_dir and isinstance(sp_dir, str)): TypeError("'sp_dir' parameter expected as string")
    # Full filepath to service principal data
    sp_name = sh.format_resource(sp_name)
    sp_path = sh.path_join(sh.path_expand(sp_dir), "{0}.json".format(sp_name))
    # Check if account subscription exists
    _log.info("checking if already signed-in...")
    # First chance to be signed-in
    _az = az.account_get(subscription)
    # _log.debug("_az: {0}".format(_az))

    # Ensure service principal credentials exist
    (service_principal, sp_changed) = login_service_principal_strategy(subscription, resource_group, key_vault, sp_name, sp_dir)

    # Ensure active directory groups/roles exist
    if sp_changed:
        (ad_group, group_changed) = ad_group_strategy(subscription, service_principal.objectId)

    if _az.is_signed_in and not service_principal:
        _log.error("failed to retrieve service principal, likely due to insufficient privileges on account, signing out...")
        az.account_logout()
        _az.is_signed_in = False
        # Prompt manual 'az login' indirectly
        _az = login_strategy(tenant, subscription, resource_group, key_vault, sp_name, sp_dir)

    if not _az.is_signed_in:
        if service_principal:
            # Attempt login with service principal credentials found, last chance to be signed-in
            _az = az.account_login(tenant, service_principal.name, service_principal.password)
            if not _az.is_signed_in:
                if retry:
                    # Will retry recursively only once
                    _log.warning("Azure login with service principal failed, saving backup and retrying...")
                    sh.file_backup(sp_path)
                    _az = login_strategy(tenant, subscription, resource_group, key_vault, sp_name, sp_dir, False)
                else:
                    _log.error("Azure login with service principal failed again, exiting...")
                    sh.process_fail()
        else:
            # Calling 'az login' in script works but the prompt in subprocess causes display issues
            # - this can occur when signed-in with service principal and needing to change own credentials
            _log.error("not signed-in, enter 'az login' to manually login before repeating your previous command")
            sh.process_fail()

    # elif used to limit recursive activity
    if sp_changed:
        # Confirm updated service principal login connects
        _log.debug("attempting login with service principal...")
        az.account_logout()
        _az.is_signed_in = False
        _az = login_strategy(tenant, subscription, resource_group, key_vault, sp_name, sp_dir)
        # No need to rename/backup SP credentials here if failed - it'll occur recursively
    elif not _az.subscription_is_default:
        # Ensure subscription is currently active
        _log.debug("activating the selected subscription...")
        account_active = az.account_set(subscription)
        if not account_active:
            _log.error("failed to activate subscription")
            sh.process_fail()

    _log.info("you are successfully signed-in Azure!")
    return _az


# ASP.NET Core NuGet Packages (https://www.nuget.org/packages/*)
def _project_packages(strat, framework):
    if not (strat and isinstance(strat, str)): TypeError("'strat' parameter expected as string")
    if not (framework and isinstance(framework, str)): TypeError("'framework' parameter expected as string")
    # Development Packages
    if framework == "netcoreapp3.1":
        dotnet_packages = [
            "Microsoft.VisualStudio.Web.BrowserLink",
            "Microsoft.CodeAnalysis.FxCopAnalyzers", # 3.x
        ]
    else:
        dotnet_packages = [
            "Microsoft.VisualStudio.Web.BrowserLink",
            # https://docs.microsoft.com/en-us/visualstudio/code-quality/migrate-from-fxcop-analyzers-to-net-analyzers
            # https://github.com/dotnet/roslyn-analyzers
            "Microsoft.CodeAnalysis.NetAnalyzers" # 5.x+
        ]
    # Database Packages
    if strat == "database" or strat == "identity":
        dotnet_packages.extend([
            # Database provider automatically includes Microsoft.EntityFrameworkCore
            "Microsoft.EntityFrameworkCore.SqlServer", # Install SQL Server database provider
            "Microsoft.EntityFrameworkCore.Design", # Install EF Core design package
            "Microsoft.EntityFrameworkCore.Tools",
            "Microsoft.VisualStudio.Web.CodeGeneration.Design",
            "Microsoft.Extensions.Logging.Debug",
            "NSwag.AspNetCore" # Swagger / OpenAPI
        ])
    # Authentication Packages
    if strat == "identity":
        dotnet_packages.extend([
            # "Microsoft.AspNetCore.Authentication.AzureAD.UI", # 3.x
            "Microsoft.AspNetCore.Diagnostics.EntityFrameworkCore",
            "Microsoft.AspNetCore.Identity.EntityFrameworkCore",
            "Microsoft.AspNetCore.Identity.UI"
            # "Install-Package Microsoft.Owin.Security.OpenIdConnect",
            # "Install-Package Microsoft.Owin.Security.Cookies",
            # "Install-Package Microsoft.Owin.Host.SystemWeb"
        ])
    dotnet_packages.sort()
    return dotnet_packages


def application_strategy(tenant, dotnet_dir, application, project, strat, environment, framework, secret_key, secret_value):
    if not _az.is_signed_in: return (False, False)
    if not (tenant and isinstance(tenant, str)): TypeError("'tenant' parameter expected as string")
    if not (dotnet_dir and isinstance(dotnet_dir, str)): TypeError("'dotnet_dir' parameter expected as string")
    if not (application and isinstance(application, str)): TypeError("'application' parameter expected as string")
    # if not isinstance(project, list): TypeError("'project' parameter expected as list")
    if not (project and isinstance(project, str)): TypeError("'project' parameter expected as string")
    if not (strat and isinstance(strat, str)): TypeError("'strat' parameter expected as string")
    if not (environment and isinstance(environment, str)): TypeError("'environment' parameter expected as string")
    if not (framework and isinstance(framework, str)): TypeError("'framework' parameter expected as string")
    app_changed = False

    # _log.info("secret_key: {0}".format(secret_key))
    # _log.info("secret_value: {0}".format(secret_value))

    # strat: [basic, database, identity]
    if strat == "identity":
        _log.info("verifying authentication...")
        # Format name for application object registration
        raw_app_name = "{0}-{1}".format(project, environment)
        app_name = sh.format_resource(raw_app_name)
        _log.info("app registration name: {0}".format(app_name))

        # Register Azure Active Directory application for project
        ad_app = az.active_directory_application_get(app_name)
        if not ad_app.appId:
            ad_app = az.active_directory_application_set(tenant, app_name)
            if not ad_app.appId:
                _log.error("failed to register active directory application")
                sh.process_fail()

        # Ensure service principal credentials exist for AD application object registration
        (service_principal, sp_changed) = service_principal_strategy(tenant, app_name, ad_app.appId)
        # _log.debug("service_principal: {0}".format(service_principal))
        # TODO: might need additional test iterations linking AD app to SP with CLI instead of portal

    # Create application/repository directory
    app_dir = sh.path_join(dotnet_dir, application)
    _log.debug("checking for application dir ({0})...".format(app_dir))
    app_dir_exists = sh.path_exists(app_dir, "d")
    if not app_dir_exists:
        _log.warning("could not locate application directory, creating...")
        sh.directory_create(app_dir)
        _log.info("successfully created application directory: {0}".format(app_dir))

    # Create ASP.NET Core solution
    solution_file = sh.path_join(dotnet_dir, application, "{0}.sln".format(application))
    _log.debug("checking for solution ({0})...".format(solution_file))
    solution_exists = sh.path_exists(solution_file, "f")
    if not solution_exists:
        _log.warning("could not locate solution, creating...")
        sln_succeeded = net.solution_new(dotnet_dir, application)
        _log.info("successfully created solution: {0}".format(sln_succeeded))
        if not sln_succeeded:
            _log.error("solution failed to be created, exiting...")
            sh.process_fail()

    _log.debug("Project Name: {0}".format(project))

    # Create project directory
    project_dir = sh.path_join(dotnet_dir, application, project)
    _log.debug("checking for project dir ({0})...".format(project_dir))
    project_dir_exists = sh.path_exists(project_dir, "d")
    if not project_dir_exists:
        _log.warning("could not locate application directory, creating...")
        sh.directory_create(project_dir)
        _log.info("successfully created application directory: {0}".format(project_dir))

    # Create ASP.NET Core project
    project_file = sh.path_join(project_dir, "{0}.csproj".format(project))
    _log.debug("checking for project ({0})...".format(project_file))
    project_exists = sh.path_exists(project_file, "f")
    if not project_exists:
        _log.warning("could not locate project, creating...")
        project_succeeded = net.project_new(dotnet_dir, application, project, strat, framework)
        _log.info("successfully created project: {0}".format(project_succeeded))
        if not project_succeeded:
            _log.error("project failed to be created, exiting...")
            sh.process_fail()

    # Add ASP.NET Core project to solution
    project_added = net.solution_project_add(dotnet_dir, application, project)
    if not project_added:
        _log.error("failed to add project: {0}".format(project))
        sh.process_fail()

    # Add NuGet packages to ASP.NET Core project
    packages_expected = _project_packages(strat, framework)
    _log.debug("NuGet packages_expected: {0}".format(packages_expected))
    packages_installed = net.project_package_list(dotnet_dir, application, project)
    _log.debug("NuGet packages_installed: {0}".format(packages_installed))
    packages_to_install = sh.list_differences(packages_expected, packages_installed)
    _log.debug("NuGet packages_to_install: {0}".format(packages_to_install))
    for package in packages_to_install:
        package_succeeded = net.project_package_add(dotnet_dir, application, project, package)
        if not package_succeeded:
            _log.error("failed to add package: {0}".format(package))
            sh.process_fail()

    # https://docs.microsoft.com/en-us/aspnet/core/security/authentication/scaffold-identity#scaffold-identity-into-a-razor-project-without-existing-authorization
    if strat == "identity":
        identity_scaffolded = net.project_identity_scaffold(project_dir)

    return (True, app_changed)


    # rg_good = az.resource_group_set(args.resource_group, args.location)
    # if not rg_good:
    #     _log.error("failed to create resource group")
    #     sh.process_fail()
    # # Create a hardened container (a vault) in Azure
    # az.key_vault_set(args.key_vault, args.resource_group)
    # # Add a [key, secret, certificate] to the key vault
    # az.key_vault_secret_set(args.key_vault, args.secret_key, args.secret_value)


    # Authorize an application to use a key or secret
    # Set key vault advanced access policies
    # Work with Hardware security modules (HSMs)
    # Delete the key vault and associated keys and secrets
    # Miscellaneous Azure Cross-Platform Command-line Interface Commands


def repository_strategy(organization, dotnet_dir, application, source="", gitignore_path="", remote_alias="origin"):
    if not (organization and isinstance(organization, str)): TypeError("'organization' parameter expected as string")
    if not (dotnet_dir and isinstance(dotnet_dir, str)): TypeError("'dotnet_dir' parameter expected as string")
    if not (application and isinstance(application, str)): TypeError("'application' parameter expected as string")
    if not isinstance(source, str): TypeError("'source' parameter expected as string")
    if not isinstance(gitignore_path, str): TypeError("'gitignore_path' parameter expected as string")
    if not (remote_alias and isinstance(remote_alias, str)): TypeError("'remote_alias' parameter expected as string")

    if source == "github":
        remote_path = "https://github.com/{0}/{1}".format(organization, application)
        _log.debug("source repository (GitHub): {0}".format(remote_path))
    elif source == "tfsgit":
        remote_path = "https://dev.azure.com/{0}/{1}".format(organization, application)
        _log.debug("source repository (Azure): {0}".format(remote_path))
        return False
    else:
        _log.error("no source repository")
        return False

    is_bare = not bool(remote_path)
    repo_descriptor = "remote, bare" if is_bare else "local, work"
    repo_changed = False

    # Create application/repository directory
    app_dir = sh.path_join(dotnet_dir, application)
    _log.debug("checking for application directory ({0})...".format(app_dir))
    app_dir_exists = sh.path_exists(app_dir, "d")
    if not app_dir_exists:
        _log.warning("could not locate application directory, creating...")
        sh.directory_create(app_dir)
        _log.info("successfully created application directory: {0}".format(app_dir))

    # Initialize Git repository directory
    repo_dir_exists = git.repo_exists(app_dir, is_bare)
    if repo_dir_exists:
        _log.debug("Successfully found {0} repository".format(repo_descriptor))
    else:
        _log.debug("Unable to locate {0} repository".format(repo_descriptor))
        display_path = app_dir if (is_bare) else "{0}/.git".format(app_dir)
        _log.info("Repository not found ({0}), initializing...".format(display_path))
        # Initialize the repository
        (repo_exists, changed) = git.repo_create(app_dir, is_bare)
        if repo_exists:
            _log.info("successfully created {0} repository!".format(repo_descriptor))
        else:
            _log.error("Unable to create {0} repository".format(repo_descriptor))
            sh.process_fail()

    # Set work repo's remote path to bare repo
    remote_result = git.work_remote(app_dir, remote_path, remote_alias)
    if not remote_result:
        _log.error("Error occurred updating remote path")
        sh.process_fail()

    # Fetch the latest meta data; increases '.git' directory size
    # git.work_fetch(app_dir)

    # Update '.gitignore' based on hash check
    if len(gitignore_path) > 0:
        file_src = gitignore_path
        file_dest = sh.path_join(app_dir, ".gitignore")
        if sh.path_exists(file_dest, "f"):
            hash_result = sh.file_match(file_src, file_dest)
            if not hash_result:
                _log.debug("'.gitignore' hashes don't match, updating...")
                update_result = sh.file_copy(file_src, file_dest)
                if update_result:
                    _log.debug("'.gitignore' was successfully updated!")
                else:
                    _log.error("'.gitignore' failed to be updated")
                    sh.process_fail()
            else:
                _log.debug("'.gitignore' is already up-to-date")
        else:
            _log.debug("'.gitignore' is missing, adding...")
            add_result = sh.file_copy(file_src, file_dest)
            if add_result:
                _log.debug("'.gitignore' was successfully added!")
            else:
                _log.error("'.gitignore' failed to be added")
                sh.process_fail()
    else:
        _log.debug("skipping '.gitignore' file check")

    return True



# --- Commands ---

# Login Azure Active Directory subscription
def login():
    # az.login_strategy(args.subscription, args.cert_path, args.tenant, args.key_vault)
    # _log.debug("1st random password: {0}".format(sh.get_random_password()))
    # _log.debug("2nd random password: {0}".format(sh.get_random_password()))
    # _log.debug("3rd random password: {0}".format(sh.get_random_password()))
    login_strategy(args.tenant, args.subscription, args.login_resource_group, args.login_key_vault, args.login_service_principal, args.login_service_principal_dir)


def secret():
    login()

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


def app_create():
    login()
    application_strategy(args.tenant, args.dotnet_dir, args.application, args.project, args.strat, args.environment, args.framework, args.secret_key, args.secret_value)
    gitignore_path = "/home/david/pc-setup/ansible_playbooks/roles/linux/apps/git/init/files/.gitignore"
    repository_strategy(args.organization, args.dotnet_dir, args.application, args.source, gitignore_path, args.remote_alias)


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
basename = "app"
args = LogArgs() # for external modules
# log_file = "/var/log/{0}.log".format(basename)
log_options = LogOptions(basename)
_log = get_logger(log_options)

if __name__ == "__main__":
    # When 'default' doesn't work, add nargs="?" and const=(same value as default)
    def parse_arguments():
        import argparse
        parser = argparse.ArgumentParser()
        # --- Subcommands of 'group' ---
        # group_subparser = parser.add_subparsers(dest="group")
        # group_subparser.add_parser("login")
        # group_subparser.add_parser("secret")
        # group_subparser.add_parser("client")
        # group_subparser.add_parser("deploy")
        # group_subparser.add_parser("pipeline")
        # --- Global defaults ---
        parser.add_argument("group", default="login", const="login", nargs="?", choices=["login", "secret", "client", "deploy", "pipeline"])
        parser.add_argument("action", default="get", const="get", nargs="?", choices=["get", "set", "remove"])
        parser.add_argument("--debug", action="store_true")
        parser.add_argument("--log-path", default="")
        # --- Account defaults ---
        parser.add_argument("--tenant", "-t", default="davidrachwalikoutlook")
        parser.add_argument("--organization", "-o", default="david-rachwalik")
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
        parser.add_argument("--environment", "-e", default="Dev")
        parser.add_argument("--location", "-l", default="southcentralus") # az account list-locations
        parser.add_argument("--resource-group", "-g", default="")
        parser.add_argument("--key-vault", "-v", default="")
        parser.add_argument("--secret-key")
        parser.add_argument("--secret-value")
        # --- ASP.NET Core Application defaults ---
        parser.add_argument("--dotnet-dir", default="/mnt/d/Repos")
        parser.add_argument("--application", "-a", default="") # solution
        # parser.add_argument('--project', nargs="*")
        parser.add_argument('--project', default="")
        parser.add_argument('--framework', default="net5.0") # "netcoreapp3.1"
        parser.add_argument("--strat", default="basic", const="basic", nargs="?", choices=["basic", "database", "identity"])
        # --- Git Repository defaults ---
        parser.add_argument('--source', default="", const="", nargs="?", choices=["github", "tfsgit"]) # tfsgit=Azure
        parser.add_argument("--remote-alias", default="origin")
        parser.add_argument("--remote-path", default="~/my_origin_repo.git")
        parser.add_argument("--gitignore-path", default="")
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
        # Configure the dotnet_boilerplate logger
        _net_log = get_logger("dotnet_boilerplate")
        set_handlers(_net_log, log_handlers)
        net.args.debug = args.debug
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
    
    elif args.group == "client":
        app_create()

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
    # app --debug login
    # app --debug --secret-key="AutoTestKey" --secret-value="007" secret
