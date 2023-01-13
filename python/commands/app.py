#!/usr/bin/env python
"""Command to control application resources (Azure, ASP.NET Core)"""

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

import argparse
from typing import Any, Dict, List, Tuple

import azure_boilerplate as az
import azure_devops_boilerplate as az_devops
import dotnet_boilerplate as net
import git_boilerplate as git
import logging_boilerplate as log
import shell_boilerplate as sh

# ------------------------ Global Azure Commands ------------------------

# --- Strategies ---


def resource_group_strategy(resource_group: str, location: str) -> Tuple[az.ResourceGroup, bool]:
    """Method to setup an Azure resource group"""
    if not AZ.is_signed_in:
        return (az.ResourceGroup(), False)
    resource_group_changed = False
    # Ensure resource group exists
    resource_group_data = az.resource_group_get(resource_group)
    if not resource_group_data.is_valid:
        LOG.warning('resource group is missing, creating...')
        resource_group_data = az.resource_group_set(resource_group, location)
        resource_group_changed = True
    LOG.debug(f'resource_group_data: {resource_group_data}')
    return (resource_group_data, resource_group_changed)


def key_vault_strategy(location: str, resource_group: str, key_vault: str):
    """Method to setup an Azure key vault"""
    if not AZ.is_signed_in:
        return (None, False)
    key_vault_changed: bool = False

    # Ensure resource group exists
    (resource_group_data, resource_group_changed) = resource_group_strategy(
        resource_group, location)
    LOG.debug(f'resource_group_data: {resource_group_data}')
    if not resource_group_data.is_valid:
        LOG.error('failed to create resource group')
        sh.fail_process()

    # Ensure key vault exists
    key_vault_data = az.key_vault_get(resource_group, key_vault)
    LOG.debug(f'key_vault_data: {key_vault_data}')
    if not key_vault_data:
        LOG.warning('key vault doesn\'t exists, creating...')
        key_vault_data = az.key_vault_set(resource_group, key_vault)
        key_vault_changed = True

    return (key_vault_data, key_vault_changed)


def ad_group_strategy(ad_member_id: str, ad_group: str = 'main-ad-group') -> Tuple[az.AdGroup, bool]:
    """Method to setup an Azure Active Directory group"""
    if not AZ.is_signed_in:
        return (az.AdGroup(), False)

    # Ensure active directory group exists
    ad_group_data: az.AdGroup = az.ad_group_get(ad_group)
    ad_group_changed: bool = False
    if not ad_group_data.is_valid:
        LOG.warning('active directory group is missing, creating...')
        (ad_group_data, ad_group_changed) = az.ad_group_set(ad_group)

    # Ensure active directory group member exists
    ad_group_member_exists: bool = az.ad_group_member_get(
        ad_group, ad_member_id)
    if not ad_group_member_exists:
        LOG.warning('active directory group member is missing, adding...')
        ad_group_member_exists = az.ad_group_member_set(ad_group, ad_member_id)

    # Ensure role is assigned to active directory group
    scope: str = f'/subscriptions/{AZ.subscription_id}'
    role_assigned: bool = az.role_assign_get(ad_group_data.id, scope)
    if not role_assigned:
        LOG.warning(
            'role is not assigned to active directory group, adding...')
        role_assigned = az.role_assign_set(ad_group_data.id, scope)

    return (ad_group_data, ad_group_changed)


def service_principal_strategy(tenant: str, service_principal: str, app_id: str) -> Tuple[az.ServicePrincipal, bool]:
    """Method to setup an Azure service principal"""
    if not AZ.is_signed_in:
        return (az.ServicePrincipal(), False)
    service_principal_changed: bool = False
    # Full filepath to service principal data
    service_principal = sh.format_resource(service_principal)
    # Ensure service principal exists
    service_principal_data: az.ServicePrincipal = az.service_principal_get(
        service_principal, tenant=tenant)
    if not service_principal_data.appId:
        LOG.debug('service principal credentials not found, creating...')
        service_principal_data = az.service_principal_set(
            service_principal, app_id)
        service_principal_changed = True
    return (service_principal_data, service_principal_changed)


def login_service_principal_strategy(location: str, resource_group: str, key_vault: str, service_principal: str, auth_dir: str) -> Tuple[az.ServicePrincipal, bool]:
    """Method to sign-in an Azure service principal"""
    service_principal_changed: bool = False
    service_principal_data: az.ServicePrincipal = az.ServicePrincipal()
    key_vault_secret_value = ''
    # Full filepath to service principal data
    service_principal = sh.format_resource(service_principal)
    service_principal_path: str = sh.join_path(
        sh.expand_path(auth_dir), f'{service_principal}.json')

    # Ensure service principal exists in Azure and local
    if sh.path_exists(service_principal_path, 'f'):
        # Gather login info from service principal JSON
        LOG.debug('service principal file exists, checking file...')
        service_principal_data = az.service_principal_get(
            service_principal, auth_dir)
    else:
        LOG.debug('service principal file missing, checking Azure...')
        if not AZ.is_signed_in:
            return (az.ServicePrincipal(), False)

        # Ensure service principal & key vault exists
        service_principal_data = az.service_principal_get(service_principal)
        LOG.debug(f'service_principal_data: {service_principal_data}')
        (key_vault_data, kv_changed) = key_vault_strategy(location, resource_group, key_vault)
        LOG.debug(f'key_vault_data: {key_vault_data}')
        if service_principal_data and key_vault_data:
            # Check for passphrase as key vault secret (to share across systems)
            key_vault_secret_value = az.key_vault_secret_get(
                key_vault, service_principal)
            # LOG.debug(f'key_vault_secret_value: {key_vault_secret_value}')
            if key_vault_secret_value:
                LOG.debug(
                    'service principal password found in key vault, saving credentials...')
                service_principal_data.password = key_vault_secret_value
            else:
                # Service principal in Azure but not local file, must reset pass to regain access
                LOG.debug(
                    'service principal successfully found, resetting credentials...')
                service_principal_data = az.service_principal_rbac_set(
                    key_vault, service_principal, True)
        else:
            LOG.debug('service principal credentials not found, creating...')
            service_principal_data = az.service_principal_rbac_set(
                key_vault, service_principal)

        # Last chance to have service principal
        if not service_principal_data:
            return (az.ServicePrincipal(), False)

        # Store password/credentials in JSON file
        az.service_principal_save(
            service_principal_path, service_principal_data)
        if not key_vault_secret_value:
            # Store password/credentials in key vault
            az.key_vault_secret_set(
                key_vault, service_principal, service_principal_data.password)

        service_principal_changed = True

        # TODO: manage service principal security groups
        # use 'az role assignment create' on groups, not service principals
        # https://docs.microsoft.com/en-us/cli/azure/create-an-azure-service-principal-azure-cli#manage-service-principal-roles

        # Ensure active directory groups/roles exist
        if service_principal_changed:
            (ad_group_data, ad_group_changed) = ad_group_strategy(service_principal_data.objectId)

        # TODO: manage service principal security access to Key Vault:
        # - manually enabled ARM for template deployment in Portal
        # - manually added the service principal as access policy in Portal
        # - examine key_vault returned from strategy

    return (service_principal_data, service_principal_changed)


def login_strategy(tenant: str, subscription: str, location: str, resource_group: str, key_vault: str, sp_name: str, auth_dir: str, retry: bool = True):
    """Method to sign-in an Azure account"""
    global AZ
    # Full filepath to service principal data
    sp_name = sh.format_resource(sp_name)
    service_principal_path = sh.join_path(
        sh.expand_path(auth_dir), f'{sp_name}.json')
    # Check if account subscription exists
    LOG.info('checking if already signed-in Azure...')
    # First chance to be signed-in
    AZ = az.account_get(subscription)
    # LOG.debug(f'AZ: {AZ}')

    # Ensure service principal credentials exist
    (service_principal, service_principal_changed) = login_service_principal_strategy(
        location, resource_group, key_vault, sp_name, auth_dir)

    if AZ.is_signed_in and not service_principal:
        LOG.error(
            'failed to retrieve service principal, likely due to insufficient privileges on account, signing out...')
        az.account_logout()
        AZ.is_signed_in = False
        # Prompt manual 'az login' indirectly
        AZ = login_strategy(tenant, subscription, location,
                            resource_group, key_vault, sp_name, auth_dir)

    if not AZ.is_signed_in:
        if service_principal:
            # Attempt login with service principal credentials found, last chance to be signed-in
            LOG.debug('attempting login with service principal...')
            AZ = az.account_login(
                tenant, service_principal.name, service_principal.password)
            if not AZ.is_signed_in:
                if retry:
                    # Will retry recursively only once
                    LOG.warning(
                        'Azure login with service principal failed, saving backup and retrying...')
                    sh.backup_file(service_principal_path)
                    AZ = login_strategy(
                        tenant, subscription, location, resource_group, key_vault, sp_name, auth_dir, False)
                else:
                    LOG.error(
                        'Azure login with service principal failed again, exiting...')
                    sh.fail_process()
        else:
            # Calling 'az login' in script works but the prompt in subprocess causes display issues
            # - this can occur when signed-in with service principal and needing to change own credentials
            LOG.error('not signed-in, enter "az login" to manually login before repeating your previous command')
            sh.fail_process()

    # elif used to limit recursive activity
    if service_principal_changed:
        # Confirm updated service principal login connects
        az.account_logout()
        AZ.is_signed_in = False
        AZ = login_strategy(tenant, subscription, location,
                            resource_group, key_vault, sp_name, auth_dir)
        # No need to rename/backup SP credentials here if failed - it'll occur recursively
    elif not AZ.subscription_is_default:
        # Ensure subscription is currently active
        LOG.debug('activating the selected subscription...')
        account_active = az.account_set(subscription)
        if not account_active:
            LOG.error('failed to activate subscription')
            sh.fail_process()

    LOG.info('you are successfully signed-in Azure!')
    return AZ


def login_devops_pat_strategy(location: str, resource_group: str, key_vault: str, auth_dir: str) -> Tuple[str, bool]:
    """Method to sign-in an Azure DevOps with PAT"""
    secret_key: str = 'main-devops-pat'
    pat_changed: bool = False
    pat_data: str = ''
    key_vault_secret_value = ''
    # Full filepath to PAT (personal access token)
    pat_path: str = sh.join_path(sh.expand_path(auth_dir), 'ado.pat')

    # Ensure user PAT exists in Azure and local
    if sh.path_exists(pat_path, 'f'):
        # Gather login info from PAT file
        LOG.debug('PAT (personal access token) exists, checking file...')
        pat_data = sh.read_file(pat_path, True)
        # LOG.debug(f'pat_data: {pat_data}')
    else:
        if not AZ.is_signed_in:
            return ('', False)
        LOG.debug('PAT (personal access token) file missing, checking Azure...')

        # Ensure PAT exists in key vault as secret
        key_vault_secret_value = az.key_vault_secret_get(key_vault, secret_key)
        if key_vault_secret_value:
            LOG.debug('PAT successfully found in key vault')
            pat_data = key_vault_secret_value
        # TODO: be able to create/reset credentials similar to login_service_principal_strategy()
        # TODO: - if missing: create PAT and save to local file
        # TODO: - if invalid/expired: revoke the PAT and delete from local file

        # Last chance to have PAT
        if not pat_data:
            return ('', False)

        # Store credentials in PAT file
        az_devops.user_save(pat_path, pat_data)

        pat_changed = True

    return (pat_data, pat_changed)


# https://docs.microsoft.com/en-us/azure/devops/cli/log-in-via-pat
# sign-in via 'az login' isn't supported, so a PAT token is required
def login_devops_strategy(user: str, location: str, resource_group: str, key_vault: str, auth_dir: str, retry: bool = True) -> bool:
    """Method to sign-in an Azure DevOps"""
    global AZ
    secret_key = 'main-devops-pat'
    key_vault_secret = ''
    # Full filepath to service principal data
    pat_path = sh.join_path(sh.expand_path(auth_dir), 'ado.pat')

    # Ensure user PAT/credentials exist
    (pat_data, pat_changed) = login_devops_pat_strategy(
        location, resource_group, key_vault, auth_dir)
    AZ.devops_pat = pat_data

    # Check if user is signed-in DevOps
    LOG.info('checking if already signed-in Azure DevOps...')
    # First chance to be signed-in
    user_is_signed_in: bool = az_devops.user_get(AZ.devops_pat, user)

    if not user_is_signed_in:
        if AZ.devops_pat:
            # Attempt login with user PAT/credentials found, last chance to be signed-in
            LOG.debug(
                'attempting DevOps login with PAT (personal access token)...')
            user_is_signed_in = az_devops.user_login(AZ.devops_pat)
            if not user_is_signed_in:
                if retry:
                    # Will retry recursively only once
                    LOG.warning(
                        'Azure DevOps login with PAT failed, saving backup and retrying...')
                    sh.backup_file(pat_path)
                    user_is_signed_in = login_devops_strategy(
                        user, location, resource_group, key_vault, auth_dir, False)
                else:
                    LOG.error(
                        'Azure DevOps login with PAT failed again, exiting...')
                    sh.fail_process()
        else:
            # - this can occur when signed-in with PAT and needing to change own credentials
            LOG.error('not signed-in DevOps, navigate the following site to manually create a PAT, go to user settings and select "Personal access tokens"')
            LOG.error('https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate')
            LOG.error(f'this PAT must be in "{key_vault}" as "{secret_key}" before repeating your previous command')
            sh.fail_process()

    if pat_changed:
        # Confirm updated PAT login connects
        az_devops.user_logout()
        user_is_signed_in = login_devops_strategy(
            user, location, resource_group, key_vault, auth_dir)
        # No need to rename/backup SP credentials here if failed - it'll occur recursively

    LOG.info('you are successfully signed-in Azure DevOps!')
    return user_is_signed_in


# ASP.NET Core NuGet Packages (https://www.nuget.org/packages/*)
def _project_packages(strat: str, framework: str) -> List[str]:
    dotnet_packages = []

    # --- Common Development Packages ---
    if framework == 'net6.0':
        dotnet_packages.extend([
            'Microsoft.CodeAnalysis.NetAnalyzers'
        ])
    elif framework == 'net5.0':
        dotnet_packages.extend([
            # https://github.com/dotnet/roslyn-analyzers
            # https://docs.microsoft.com/en-us/visualstudio/code-quality/migrate-from-fxcop-analyzers-to-net-analyzers
            'Microsoft.CodeAnalysis.NetAnalyzers',  # 5.x+
            'Microsoft.VisualStudio.Web.BrowserLink'
        ])
    elif framework == 'netcoreapp3.1':
        dotnet_packages.extend([
            'Microsoft.CodeAnalysis.FxCopAnalyzers',  # 3.x
            # 'Microsoft.Extensions.Logging.Debug', # No longer required; included in 'Microsoft.AspNetCore.App'
            'Microsoft.VisualStudio.Web.BrowserLink'
        ])

    # --- Database Packages ---
    # Packages needed for scaffolding: [Microsoft.VisualStudio.Web.CodeGeneration.Design, Microsoft.EntityFrameworkCore.SqlServer]
    if strat == 'database' or strat == 'identity' or strat == 'api':
        if framework in ['netcoreapp3.1', 'net5.0', 'net6.0']:
            dotnet_packages.extend([
                'Microsoft.AspNetCore.Diagnostics.EntityFrameworkCore',
                'Microsoft.EntityFrameworkCore.Tools',
                'Microsoft.EntityFrameworkCore.Design',     # Install EF Core design package
                'Microsoft.VisualStudio.Web.CodeGeneration.Design',
                # Database provider automatically includes Microsoft.EntityFrameworkCore
                # Install SQL Server database provider
                'Microsoft.EntityFrameworkCore.SqlServer'
                # 'Microsoft.EntityFrameworkCore.Sqlite'      # Install SQLite database provider
            ])

    # --- Authentication Packages ---
    if strat == 'identity':
        # 'Microsoft.Owin.Security.OpenIdConnect',
        # 'Microsoft.Owin.Security.Cookies',
        # 'Microsoft.Owin.Host.SystemWeb'
        if framework in ['net5.0', 'net6.0']:
            dotnet_packages.extend([
                'Microsoft.AspNetCore.Identity.EntityFrameworkCore',
                'Microsoft.AspNetCore.Identity.UI'
            ])
        elif framework == 'netcoreapp3.1':
            dotnet_packages.extend([
                'Microsoft.AspNetCore.Authentication.AzureAD.UI'  # 3.x
            ])

    # --- API Packages ---
    if strat == 'api':
        if framework in ['netcoreapp3.1', 'net5.0', 'net6.0']:
            dotnet_packages.extend([
                # 'NSwag.AspNetCore' # Swagger / OpenAPI
                'Swashbuckle.AspNetCore'
            ])

    dotnet_packages.sort()
    return dotnet_packages


def application_strategy(tenant: str, root_dir: str, solution: str, project: str, strat: str, environment: str,
                         framework: str, secret_key: str = '', secret_value: str = '') -> Tuple[bool, bool]:
    """Method to setup an Azure application"""
    if not AZ.is_signed_in:
        return (False, False)
    app_changed = False
    # Determine solution scenario (if a solution directory should exist)
    use_solution_dir = bool(solution and isinstance(solution, str))
    app_dir = sh.join_path(
        root_dir, solution) if use_solution_dir else sh.join_path(root_dir, project)

    # LOG.info(f"secret_key: {secret_key}")
    # LOG.info(f"secret_value: {secret_value}")

    # strat: [basic, database, identity, api]
    if strat == 'identity':
        LOG.info('verifying authentication...')
        # Format name for application object registration
        raw_app_name = f'{project}-{environment}'
        app_name = sh.format_resource(raw_app_name)
        LOG.info(f'app registration name: {app_name}')

        # Register Azure Active Directory application for project
        ad_app = az.active_directory_application_get(app_name)
        if not ad_app.appId:
            ad_app = az.active_directory_application_set(tenant, app_name)
            if not ad_app.appId:
                LOG.error('failed to register active directory application')
                sh.fail_process()

        # Ensure service principal credentials exist for AD application object registration
        (service_principal, service_principal_changed) = service_principal_strategy(
            tenant, app_name, ad_app.appId)
        # LOG.debug(f'service_principal: {service_principal}')
        # TODO: might need additional test iterations linking AD app to SP with CLI instead of portal

    # # Create solution/repository directory
    # LOG.debug(f'checking for solution dir ({app_dir})...')
    # app_dir_exists = sh.path_exists(app_dir, 'd')
    # if not app_dir_exists:
    #     LOG.warning('could not locate solution directory, creating...')
    #     sh.create_directory(app_dir)
    #     LOG.info(f'successfully created solution directory: {app_dir}')

    LOG.debug(f'Project Name: {project}')

    # Create project directory
    project_dir: str = sh.join_path(
        app_dir, project) if use_solution_dir else app_dir
    LOG.debug(f'checking for project dir ({project_dir})...')
    project_dir_exists: bool = sh.path_exists(project_dir, 'd')
    if not project_dir_exists:
        LOG.warning('could not locate project directory, creating...')
        sh.create_directory(project_dir)
        LOG.info(
            f'successfully created project directory: {project_dir}')

    # Create ASP.NET Core project
    project_file: str = sh.join_path(project_dir, f'{project}.csproj')
    LOG.debug(f'checking for project ({project_file})...')
    project_exists: bool = sh.path_exists(project_file, 'f')
    if not project_exists:
        LOG.warning('could not locate project, creating...')
        project_succeeded: bool = net.project_new(
            tenant, project_dir, strat, framework)
        LOG.info(f'successfully created project: {project_succeeded}')
        if not project_succeeded:
            LOG.error('project failed to be created, exiting...')
            sh.fail_process()

    # Create ASP.NET Core solution
    solution_file: str = sh.join_path(app_dir, f'{solution}.sln') if use_solution_dir else sh.join_path(
        app_dir, f'{project}.sln')
    LOG.debug(f'checking for solution ({solution_file})...')
    solution_exists: bool = sh.path_exists(solution_file, 'f')
    if not solution_exists:
        LOG.warning('could not locate solution, creating...')
        sln_succeeded = net.solution_new(
            app_dir, solution) if use_solution_dir else net.solution_new(app_dir, project)
        LOG.info(f'successfully created solution: {sln_succeeded}')
        if not sln_succeeded:
            LOG.error('solution failed to be created, exiting...')
            sh.fail_process()

    # Add ASP.NET Core project to solution
    project_added: bool = net.solution_project_add(solution_file, project_file)
    if not project_added:
        LOG.error(f'failed to add project: {project}')
        sh.fail_process()

    # Add NuGet packages to ASP.NET Core project
    packages_expected: List[str] = _project_packages(strat, framework)
    # LOG.debug(f'NuGet packages_expected: {packages_expected}')
    packages_installed: List[str] = net.project_package_list(project_dir)
    # LOG.debug(f'NuGet packages_installed: {packages_installed}')
    packages_to_install: List[str] = sh.list_differences(
        packages_expected, packages_installed)
    LOG.debug(f'NuGet packages_to_install: {packages_to_install}')
    for package in packages_to_install:
        package_succeeded: bool = net.project_package_add(project_dir, package)
        if not package_succeeded:
            LOG.error(f'failed to add package: {package}')
            sh.fail_process()

    # https://docs.microsoft.com/en-us/aspnet/core/security/authentication/scaffold-identity#scaffold-identity-into-a-razor-project-without-existing-authorization
    if strat == 'identity':
        identity_scaffolded = net.project_identity_scaffold(project_dir)

    return (True, app_changed)


def repository_strategy(organization: str, root_dir: str, app_name: str, source: str = '', gitignore_path: str = '', remote_alias: str = 'origin') -> bool:
    """Method to setup a GitHub or Azure repository"""
    if source == 'github':
        remote_path = f'https://github.com/{organization}/{app_name}'
        LOG.debug(f'source repository (GitHub) remote: {remote_path}')
    elif source == 'tfsgit':
        remote_path = f'https://dev.azure.com/{organization}/{app_name}'
        LOG.debug(f'source repository (Azure) remote: {remote_path}')
        return False
    else:
        LOG.error('no source repository')
        return False

    is_bare: bool = not bool(remote_path)
    repo_descriptor: str = 'remote, bare' if is_bare else 'local, work'
    repo_changed: bool = False

    # Create repository directory
    app_dir: str = sh.join_path(root_dir, app_name)
    LOG.debug(f'checking for repository directory ({app_dir})...')
    app_dir_exists: bool = sh.path_exists(app_dir, 'd')
    if not app_dir_exists:
        LOG.warning('could not locate repository directory, creating...')
        sh.create_directory(app_dir)
        LOG.info(f'successfully created repository directory: {app_dir}')

    # Initialize Git repository directory
    repo_dir_exists: bool = git.repo_exists(app_dir, is_bare)
    if repo_dir_exists:
        LOG.debug(f'Successfully found {repo_descriptor} repository')
    else:
        LOG.debug(f'Unable to locate {repo_descriptor} repository')
        display_path: str = app_dir if (
            is_bare) else f'{app_dir}/.git'
        LOG.info(
            f'Repository not found ({display_path}), initializing...')
        # Initialize the repository
        (repo_exists, repo_changed) = git.repo_create(app_dir, is_bare)
        if repo_exists:
            LOG.info(f'successfully created {repo_descriptor} repository!')
        else:
            LOG.error(
                f'Unable to create {repo_descriptor} repository')
            sh.fail_process()

    # Set work repo's remote path to bare repo
    remote_result = git.work_remote(app_dir, remote_path, remote_alias)
    if not remote_result:
        LOG.error('Error occurred updating remote path')
        sh.fail_process()

    # Fetch the latest meta data; increases '.git' directory size
    # git.work_fetch(app_dir)

    # Update '.gitignore' based on hash check
    if len(gitignore_path) > 0:
        file_src = gitignore_path
        file_dest = sh.join_path(app_dir, '.gitignore')
        if sh.path_exists(file_dest, 'f'):
            hash_result = sh.match_file(file_src, file_dest)
            if not hash_result:
                LOG.debug('".gitignore" hashes don\'t match, updating...')
                update_result = sh.copy_file(file_src, file_dest)
                if update_result:
                    LOG.debug('".gitignore" was successfully updated!')
                else:
                    LOG.error('".gitignore" failed to be updated')
                    sh.fail_process()
            else:
                LOG.debug('".gitignore" is already up-to-date')
        else:
            LOG.debug('".gitignore" is missing, adding...')
            add_result = sh.copy_file(file_src, file_dest)
            if add_result:
                LOG.debug('".gitignore" was successfully added!')
            else:
                LOG.error('".gitignore" failed to be added')
                sh.fail_process()
    else:
        LOG.debug('skipping ".gitignore" file check')

    return True


# https://docs.microsoft.com/en-us/azure/azure-resource-manager/templates/deploy-cli#parameters
def _json_to_parameters(parameters: Dict[str, Dict[str, Any]]) -> List[str]:
    out_parameters: List[str] = []
    if not parameters:
        return out_parameters
    # Convert parameters JSON to CLI-ready parameters
    for item in parameters.items():
        # LOG.debug(f'parameters item: {item}')
        # LOG.debug(f'parameters key: {item[0]}')
        if 'value' in item[1]:
            # LOG.debug(f'parameters value: {item[1]["value"]}')
            out_parameters.append(f'{item[0]}={item[1]["value"]}')
    return out_parameters


def deployment_group_strategy(tenant: str, sp_name: str, project: str, environment: str, location: str, arm: str) -> Tuple[bool, bool]:
    """Method to setup an Azure deployment group"""
    # if not AZ.is_signed_in: return (az.ResourceGroup(), False)
    deployment_succeeded: bool = False
    deployment_changed: bool = False
    rg_name: str = sh.format_resource(f'{project}-{environment}')
    LOG.debug(f'rg_name: {rg_name}')

    # Ensure resource group exists
    (resource_group, resource_group_changed) = resource_group_strategy(rg_name, location)
    if not resource_group.is_valid:
        LOG.error('failed to create resource group')
        sh.fail_process()

    # Azure Resource Manager steps
    rm_root_path: str = '~/pc-setup/ansible_playbooks/roles/azure/resource_manager/deploy/templates'
    template_path: str = sh.join_path(rm_root_path, arm, 'azuredeploy.json')
    parameters_path: str = sh.join_path(
        rm_root_path, arm, 'azuredeploy.parameters.json')
    parameters_file: str = sh.read_file(parameters_path)
    parameters_json: Dict[str, Dict[str, Any]] = az.ArmParameters(parameters_file).content

    # When 'objectId' is in parameters, replace its value with service principal's objectId
    if ('objectId' in parameters_json and 'value' in parameters_json['objectId']):
        # LOG.debug(f'parameters_json objectId: {parameters_json['objectId']['value']}')
        service_principal = az.service_principal_get(sp_name)
        # LOG.debug(f'service_principal: {service_principal}')
        if service_principal.objectId:
            parameters_json['objectId']['value'] = service_principal.objectId
            # LOG.debug(f'parameters_json objectId: {parameters_json['objectId']['value']}')
            # LOG.debug(f'parameters_json: {parameters_json}')

    # Convert parameters JSON to CLI-ready parameters
    LOG.debug(f'parameters_json: {parameters_json}')
    parameters: List[str] = _json_to_parameters(parameters_json)
    LOG.debug(f'parameters: {parameters}')

    # Ensure deployment group template is valid
    deploy_valid: bool = az.deployment_group_valid(
        resource_group.name, template_path, parameters)
    if deploy_valid:
        LOG.info('deployment validation has succeeded!')
        deployment_succeeded = az.deployment_group_set(
            resource_group.name, template_path, parameters)
        if deployment_succeeded:
            LOG.info('deployment to resource group has succeeded!')
            deployment_changed = True
        else:
            LOG.warning('deployment to resource group has failed')
    else:
        LOG.warning('deployment validation has failed')
    return (deployment_succeeded, deployment_changed)


# --- Commands ---

# Login Azure Active Directory subscription
def login():
    """Method to perform actions to sign-in Azure"""
    login_strategy(ARGS.tenant, ARGS.subscription, ARGS.location, ARGS.login_resource_group,
                   ARGS.login_key_vault, ARGS.login_service_principal, ARGS.login_service_principal_dir)
    # Sign into Azure DevOps using PAT; TODO: automatically refresh upon expire
    login_devops_strategy(ARGS.login_devops_user, ARGS.location, ARGS.login_resource_group,
                          ARGS.login_key_vault, ARGS.login_service_principal_dir)


def secret():
    """Method to perform actions to create an Azure key vault secret"""
    login()
    key_vault_strategy(ARGS.location, ARGS.resource_group, ARGS.key_vault)
    # Add a [key, secret, certificate] to vault (certificates have annual renewal costs)
    # az.key_vault_secret_set(ARGS.key_vault, ARGS.secret_key, ARGS.secret_value)
    # Set key vault advanced access policies


def app_create():
    """Method to perform actions to create an Azure application"""
    login()
    application_strategy(ARGS.tenant, ARGS.dotnet_dir, ARGS.solution, ARGS.project,
                         ARGS.strat, ARGS.environment, ARGS.framework, ARGS.secret_key, ARGS.secret_value)
    gitignore_path = '/home/david/pc-setup/ansible_playbooks/roles/linux/apps/git/init/files/.gitignore'
    # Determine scenario (if repo is inside solution or project directory)
    use_solution_dir = bool(ARGS.solution and isinstance(ARGS.solution, str))
    app_name = ARGS.solution if use_solution_dir else ARGS.project
    repository_strategy(ARGS.organization, ARGS.dotnet_dir,
                        app_name, ARGS.source, gitignore_path, ARGS.remote_alias)


def deploy():
    """Method to perform actions to deploy an application to Azure"""
    login()
    # Deploy ARM templates to resource group
    deployment_group_strategy(ARGS.tenant, ARGS.login_service_principal,
                              ARGS.project, ARGS.environment, ARGS.location, ARGS.arm)
    # Example deployment resource scenarios:
    # - resource group, app service plan, web app service
    # - resource group, app service plan, web app service, sql server, sql database, connection


def pipeline():
    """Method to perform actions to create an Azure pipeline"""
    login()
    LOG.debug('<mock "pipeline" action> -- to be added later if az command gains more pipelines methods')
    # Project pipeline example scenarios:
    # - build csproj, deploy Python (pip) packages
    # - build csproj, deploy NuGet packages
    # - build csproj, deploy ARM templates
    # - build csproj, deploy .zip file to web app service
    # - build csproj, deploy .sql file to sql database


# ------------------------ Main program ------------------------

# Initialize the logger
BASENAME = 'app'
ARGS: argparse.Namespace = argparse.Namespace()  # for external modules
# log_file = f'/var/log/{BASENAME}.log'
LOG: log.Logger = log.get_logger(BASENAME)

if __name__ == '__main__':
    # When 'default' doesn't work, add nargs="?" and const=(same value as default)
    def parse_arguments():
        """Method that parses arguments provided"""
        parser = argparse.ArgumentParser()
        # --- Subcommands of 'group' ---
        # group_subparser = parser.add_subparsers(dest="group")
        # group_subparser.add_parser("login")
        # group_subparser.add_parser("secret")
        # group_subparser.add_parser("client")
        # group_subparser.add_parser("deploy")
        # group_subparser.add_parser("pipeline")
        # --- Global defaults ---
        parser.add_argument('group', default='login', const='login', nargs='?', choices=[
                            'login', 'secret', 'client', 'deploy', 'pipeline'])
        parser.add_argument('action', default='get', const='get',
                            nargs='?', choices=['get', 'set', 'remove'])
        parser.add_argument('--debug', action='store_true')
        parser.add_argument('--log-path', default='')
        # --- Account defaults ---
        parser.add_argument('--tenant', '-t', default='davidrachwalikoutlook')
        parser.add_argument('--organization', '-o', default='david-rachwalik')
        parser.add_argument('--subscription', '-s', default='Pay-As-You-Go')
        # parser.add_argument('--cert-path', default='~/.local/az_cert.pem')
        # ~/.local/az_service_principals/{service-principal}.json
        service_principal_dir = '~/.local/az_service_principals'
        parser.add_argument('--service-principal-dir',
                            default=service_principal_dir)
        parser.add_argument('--service-principal', default='')
        # --- Login defaults ---
        parser.add_argument('--login-service-principal-dir',
                            default=service_principal_dir)
        parser.add_argument('--login-service-principal',
                            default='main-rbac-sp')
        parser.add_argument('--login-resource-group', '-G', default='Main')
        parser.add_argument('--login-key-vault', '-V', default='main-keyvault')
        parser.add_argument('--login-devops-user', '-U',
                            default='david-rachwalik@outlook.com')
        # --- Azure Resource defaults ---
        parser.add_argument('--environment', '-e', default='Dev')
        # az account list-locations
        parser.add_argument('--location', '-l', default='southcentralus')
        parser.add_argument('--resource-group', '-g', default='')
        parser.add_argument('--key-vault', '-v', default='')
        parser.add_argument('--secret-key')
        parser.add_argument('--secret-value')
        parser.add_argument('--arm', default='')
        # --- ASP.NET Core Application defaults ---
        parser.add_argument('--dotnet-dir', default='/mnt/e/Repos')
        parser.add_argument('--solution', '-a', default='')
        parser.add_argument('--project', '-p', default='')
        # 'netcoreapp3.1', 'net5.0', 'net6.0'
        parser.add_argument('--framework', '-f', default='net6.0')
        parser.add_argument('--strat', default='basic', const='basic',
                            nargs='?', choices=['basic', 'database', 'identity', 'api'])
        # parser.add_argument('--template', default='console', const='console', nargs='?', choices=, ['console', 'webapp', 'webapi', 'xunit'])
        # parser.add_argument('--identity', default='None', const='None', nargs='?', choices=, ['None', 'SingleOrg', 'MultiOrg'])
        # --- Git Repository defaults ---
        parser.add_argument('--source', default='', const='',
                            nargs='?', choices=['github', 'tfsgit'])  # tfsgit=Azure
        parser.add_argument('--remote-alias', default='origin')
        parser.add_argument('--remote-path', default='~/my_origin_repo.git')
        parser.add_argument('--gitignore-path', default='')
        return parser.parse_args()
    ARGS = parse_arguments()

    #  Configure the main logger
    LOG_HANDLERS = log.default_handlers(ARGS.debug, ARGS.log_path)
    log.set_handlers(LOG, LOG_HANDLERS)
    if ARGS.debug:
        # Configure the shell_boilerplate logger
        _sh_log = log.get_logger('shell_boilerplate')
        log.set_handlers(_sh_log, LOG_HANDLERS)
        sh.ARGS.debug = ARGS.debug
        # Configure the dotnet_boilerplate logger
        _net_log = log.get_logger('dotnet_boilerplate')
        log.set_handlers(_net_log, LOG_HANDLERS)
        net.ARGS.debug = ARGS.debug
        # Configure the azure_boilerplate logger
        _az_log = log.get_logger('azure_boilerplate')
        log.set_handlers(_az_log, LOG_HANDLERS)
        az.ARGS.debug = ARGS.debug
        # Configure the azure_devops_boilerplate logger
        _az_devops_log = log.get_logger('azure_devops_boilerplate')
        log.set_handlers(_az_devops_log, LOG_HANDLERS)
        az_devops.ARGS.debug = ARGS.debug

    # ------------------------ Business Logic (group/action) ------------------------

    LOG.debug(f'ARGS: {ARGS}')
    # LOG.debug(f''{ARGS.group}' group detected')
    # LOG.debug(f''{ARGS.action}' action detected')
    LOG.debug('--------------------------------------------------------')
    AZ = az.Account()

    # --- Run Actions ---

    if ARGS.group == 'login':
        login()

    elif ARGS.group == 'secret':
        secret()

    elif ARGS.group == 'client':
        app_create()

    elif ARGS.group == 'deploy':
        deploy()

    elif ARGS.group == 'pipeline':
        pipeline()

    # If we get to this point, assume all went well
    LOG.debug('--------------------------------------------------------')
    LOG.debug('--- end point reached :3 ---')
    sh.exit_process()

    # :: Usage Example ::
    # setup --tags "py" --skip-tags "windows"
    # app --debug login
    # app --debug --secret-key="AutoTestKey" --secret-value="007" secret
