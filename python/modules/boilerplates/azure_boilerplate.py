#!/usr/bin/env python
"""Common logic for Python Azure interactions"""

# --- Global Azure Classes ---
# Account:                      is_signed_in, tenant_id, account_user, subscription, subscription_id, subscription_is_default
# ServicePrincipal:             name, appId, password

# --- Global Azure Methods ---
# account:                      account_get, account_list, account_logout, account_login, account_set
# active directory group:       ad_group_get, ad_group_set
# active directory role:        ad_role_get, ad_role_set
# service principal:            service_principal_get, service_principal_rbac_set, service_principal_save
# resource group:               resource_group_get, resource_group_set, resource_group_delete
# key vault:                    key_vault_get, key_vault_set
# key vault secret:             key_vault_secret_get, key_vault_secret_set, key_vault_secret_download
# active directory:             active_directory_application_get, active_directory_application_set
# deployment group:             deployment_group_valid, deployment_group_get, deployment_group_set

# TODO:
# webapp service:               app_set, app_get
# app service plan:             plan_set, plan_get
# resource manager:             rm_set, rm_get
# pipelines:                    pipeline_set, pipeline_get
# SQL database:                 sql_db_set, sql_db_get

# import json, time, re
import argparse
from typing import List, Optional, Tuple

import logging_boilerplate as log
import shell_boilerplate as sh

# ------------------------ Classes ------------------------


class AzureBase(object):
    """Class that tracks baseline Azure variables"""

    def __repr__(self):
        return vars(self)

    def __str__(self):
        return str(vars(self))


class Account(AzureBase):
    """Class that tracks Azure account"""

    def __init__(self, obj=""):
        self.is_signed_in: bool = False
        self.tenant_id: str = ""  # active directory
        self.account_user: str = ""  # Microsoft account (*@outlook.com, *@hotmail.com)
        self.subscription: str = ""
        self.subscription_id: str = ""
        self.subscription_is_default: bool = False
        self.devops_pat: str = ""

        # Business logic for parsing
        if obj and isinstance(obj, str):
            obj = sh.from_json(obj)
        # Sometimes the output is a list (e.g. 'az login')
        # TODO: search by subscription name instead of always first result
        if obj and isinstance(obj, list):
            obj = obj[0]
        if sh.is_json_parse(obj):
            self.tenant_id = obj.tenantId
            self.account_user = obj.user.name
            self.subscription = obj.name
            self.subscription_id = obj.id
            self.subscription_is_default = obj.isDefault
            self.is_signed_in = bool(self.tenant_id and self.subscription_id)


class AdGroup(AzureBase):
    """Class that tracks Azure Active Directory group"""

    def __init__(self, obj=""):
        self.is_valid: bool = False
        self.name: str = ""

        # Business logic for parsing
        if obj and isinstance(obj, str):
            obj = sh.from_json(obj)
        if sh.is_json_parse(obj):
            self.name = obj.displayName
            self.mail_nickname = obj.mailNickname
            self.type = obj.objectType  # Group
            self.id = obj.objectId
            self.is_valid = bool(self.name)


# NOTE: match attribute names to stdout for consistent JSON serialization
class ServicePrincipal(AzureBase):
    """Class that tracks Azure service principal"""

    def __init__(self, obj="", sp_name=""):
        self.name: str = sp_name
        self.appId: str = ""
        self.objectId: str = ""
        self.password: str = ""

        # Business logic for parsing
        if obj and isinstance(obj, str):
            obj = sh.from_json(obj)
        if sh.is_json_parse(obj):
            keys = obj.keys()

            # keys for 'az ad sp show', 'az ad sp create-for-rbac', 'az ad sp credential reset'
            # - [name, appId,    password,     tenant]
            # keys for 'az ad sp create-for-rbac --sdk-auth'
            # - [      clientId, clientSecret, tenantId]

            if "name" in keys:
                self.name = sh.path_basename(obj.name)
            if "appId" in keys:
                self.appId = obj.appId
            if "objectId" in keys:
                self.objectId = obj.objectId
            if "password" in keys:
                self.password = obj.password


class ResourceGroup(AzureBase):
    """Class that tracks Azure resource group"""

    def __init__(self, obj=""):
        self.is_valid: bool = False
        self.name: str = ""
        self.location: str = ""

        # Business logic for parsing
        if obj and isinstance(obj, str):
            obj = sh.from_json(obj)
        if sh.is_json_parse(obj):
            self.location = obj.location
            self.name = obj.name
            self.is_valid = bool(self.location and self.name)


class ActiveDirectoryApplication(AzureBase):
    """Class that tracks Azure Active Directory application"""

    def __init__(self, obj=""):
        self.name: str = ""
        self.appId: str = ""  # client_id

        # Business logic for parsing
        if obj and isinstance(obj, str):
            obj = sh.from_json(obj)
        if sh.is_json_parse(obj):
            self.appId = obj.appId
            self.name = obj.displayName
            self.domain = obj.homepage
            self.identifierUri = obj.identifierUris[0]
            self.objectId = obj.objectId
            self.objectType = obj.objectType
            self.publisherDomain = obj.publisherDomain
            self.replyUrl = obj.replyUrls[0]
            self.signInAudience = obj.signInAudience
            self.wwwHomepage = obj.wwwHomepage


class ArmParameters(AzureBase):
    """Class that tracks Azure Resource Manager parameters"""

    def __init__(self, obj=""):
        self.content = {}
        # Business logic for parsing
        if obj and isinstance(obj, str):
            obj = sh.from_json(obj)
        if sh.is_json_parse(obj):
            self.content = obj.parameters
            if not self.content:
                self.content = {}

    def __repr__(self):
        return self.content

    def __str__(self):
        return str(self.content)


# ------------------------ Global Methods ------------------------

# --- Account/Subscription Commands ---
# https://docs.microsoft.com/en-us/cli/azure/account

def account_get(subscription: str) -> Account:
    """Method that fetches Azure account"""
    command: List[str] = ["az", "account", "show", f"--subscription={subscription}"]
    sh.print_command(command)
    (stdout, stderr, rc) = sh.run_subprocess(command)
    # sh.log_subprocess(LOG, stdout, stderr, rc, debug=ARGS.debug)
    if rc != 0:
        return Account()
    # Return the parsed account data
    results: Account = Account(stdout)
    # LOG.debug("fresults: {results}")
    return results


def account_list() -> Account:
    """Method that lists Azure accounts"""
    command: List[str] = ["az", "account", "list", "--all"]
    sh.print_command(command)
    (stdout, stderr, rc) = sh.run_subprocess(command)
    # sh.log_subprocess(LOG, stdout, stderr, rc, debug=ARGS.debug)
    if rc != 0:
        return Account()
    # Return the parsed account data
    results: Account = Account(stdout)
    # LOG.debug("fresults: {results}")
    return results


def account_logout() -> bool:
    """Method that signs out of Azure account"""
    command: List[str] = ["az", "logout"]
    sh.print_command(command)
    (stdout, stderr, rc) = sh.run_subprocess(command)
    # sh.log_subprocess(LOG, stdout, stderr, rc, debug=ARGS.debug)
    return rc == 0


# https://docs.microsoft.com/en-us/cli/azure/reference-index#az_login
# Login with username (service principal) and password (client secret/certificate)
def account_login(tenant: str = "", name: str = "", password: str = "") -> Account:
    """Method that signs into Azure account"""
    command: List[str] = ["az", "login"]
    # az login --service-principal -u <app-url> -p <password-or-cert> --tenant <tenant>
    if tenant and name and password:
        command.append("--service-principal")
        command.append(f"--tenant={tenant}.onmicrosoft.com")
        command.append(f"--username=http://{name}")
        command.append(f"--password={password}")
        command.append("--allow-no-subscriptions")
    # Print password-safe version of command
    sh.print_command(command, "--password=")
    (stdout, stderr, rc) = sh.run_subprocess(command)
    # sh.log_subprocess(LOG, stdout, stderr, rc, debug=ARGS.debug)
    if rc != 0:
        return Account()
    # Return the parsed account data
    results: Account = Account(stdout)
    # LOG.debug("fresults: {results}")
    return results


def account_set(subscription: str) -> bool:
    """Method that sets the default Azure account"""
    command: List[str] = ["az", "account", "set", f"--subscription={subscription}"]
    sh.print_command(command)
    (stdout, stderr, rc) = sh.run_subprocess(command)
    # sh.log_subprocess(LOG, stdout, stderr, rc, debug=ARGS.debug)
    return rc == 0


# --- Active Directory (AD) Group Commands ---
# https://docs.microsoft.com/en-us/cli/azure/ad/group

def ad_group_get(name: str) -> AdGroup:
    """Method that fetches Azure Active Directory group"""
    command: List[str] = ["az", "ad", "group", "show", f"--group={name}"]
    sh.print_command(command)
    (stdout, stderr, rc) = sh.run_subprocess(command)
    # sh.log_subprocess(LOG, stdout, stderr, rc, debug=ARGS.debug)
    ad_group: AdGroup = AdGroup(stdout)
    LOG.debug(f"ad_group: {ad_group}")
    return ad_group


def ad_group_set(name: str) -> Tuple[AdGroup, bool]:
    """Method that sets the Azure Active Directory group"""
    ad_group: AdGroup = AdGroup()
    group_changed: bool = False
    command: List[str] = ["az", "ad", "group", "create",
                          f"--display-name={name}", f"--mail-nickname={name}"]
    sh.print_command(command)
    (stdout, stderr, rc) = sh.run_subprocess(command)
    # sh.log_subprocess(LOG, stdout, stderr, rc, debug=ARGS.debug)
    if rc == 0:
        ad_group = AdGroup(stdout)
        group_changed = True
    LOG.debug(f"ad_group: {ad_group}")
    return (ad_group, group_changed)


# --- Active Directory (AD) Group Member Commands ---
# https://docs.microsoft.com/en-us/cli/azure/ad/group/member

def ad_group_member_get(name: str, member_id: str) -> bool:
    """Method that fetches Azure Active Directory group member"""
    command: List[str] = ["az", "ad", "group", "member", "check",
                          f"--group={name}", f"--member-id={member_id}", "--query=value"]
    sh.print_command(command, "--member-id=")
    (stdout, stderr, rc) = sh.run_subprocess(command)
    # sh.log_subprocess(LOG, stdout, stderr, rc, debug=ARGS.debug)
    return rc == 0 and stdout == "true"


def ad_group_member_set(name: str, member_id: str) -> bool:
    """Method that sets Azure Active Directory group member"""
    command: List[str] = ["az", "ad", "group", "member", "add",
                          f"--group={name}", f"--member-id={member_id}"]
    sh.print_command(command, "--member-id=")
    (stdout, stderr, rc) = sh.run_subprocess(command)
    # sh.log_subprocess(LOG, stdout, stderr, rc, debug=ARGS.debug)
    return rc == 0


# --- Role Assignment Commands ---
# https://docs.microsoft.com/en-us/cli/azure/role/assignment
# https://docs.microsoft.com/en-us/azure/role-based-access-control/built-in-roles
# https://docs.microsoft.com/en-us/azure/role-based-access-control/role-assignments-cli

def role_assign_get(assignee_id: str, scope: str = "", role: str = "Contributor") -> bool:
    """Method that fetches Azure role"""
    # NOTE: do not wrap --role value in '', gets evaluated as part of string
    command: List[str] = ["az", "role", "assignment", "list",
                          f"--assignee={assignee_id}",
                          f"--role={role}", f"--scope={scope}",
                          "--include-inherited", "--include-groups", "--query=[0]"
                          ]
    sh.print_command(command, "--scope=")
    (stdout, stderr, rc) = sh.run_subprocess(command)
    # sh.log_subprocess(LOG, stdout, stderr, rc, debug=ARGS.debug)
    return rc == 0


def role_assign_set(assignee_id: str, scope: str = "", role: str = "Contributor") -> bool:
    """Method that assigns Azure role"""
    # NOTE: do not wrap --role value in '', gets evaluated as part of string
    command: List[str] = ["az", "role", "assignment", "create",
                          f"--assignee={assignee_id}",
                          f"--role={role}", f"--scope={scope}"
                          ]
    sh.print_command(command, "--scope=")
    (stdout, stderr, rc) = sh.run_subprocess(command)
    sh.log_subprocess(LOG, stdout, stderr, rc, debug=ARGS.debug)
    return rc == 0


# --- Service Principal Commands ---
# https://docs.microsoft.com/en-us/cli/azure/ad/sp

# Always use service principal name (not id)
def service_principal_get(sp_name: str, sp_dir: str = "", tenant: str = "") -> ServicePrincipal:
    """Method that fetches Azure service principal"""
    # Full filepath to service principal data
    if not sh.is_valid_resource(sp_name):
        LOG.error("'sp_name' parameter expected as valid resource name")
        sh.fail_process()
    # Gather login info from service principal
    if sp_dir:
        LOG.debug("gathering service principal credentials from file...")
        sp_path = sh.join_path(sh.expand_path(sp_dir), f"{sp_name}.json")
        stdout = sh.read_file(sp_path)
    else:
        LOG.debug("gathering service principal from Azure...")
        # if not sp_name.startswith("http://"): sp_name = f"http://{sp_name}"
        if tenant:
            command = ["az", "ad", "sp", "show", f"--id=https://{tenant}.onmicrosoft.com/{sp_name}"]
        else:
            command = ["az", "ad", "sp", "show", f"--id=http://{sp_name}"]
        sh.print_command(command)
        (stdout, stderr, rc) = sh.run_subprocess(command)
        # sh.log_subprocess(LOG, stdout, stderr, rc, debug=ARGS.debug)
        if rc != 0:
            return ServicePrincipal()
    # Return the parsed service principal data
    service_principal: ServicePrincipal = ServicePrincipal(stdout, sp_name)
    # LOG.debug(f"service_principal: {service_principal}")
    return service_principal


def service_principal_set(sp_name: str, obj_id: str) -> ServicePrincipal:
    """Method that sets a Azure service principal"""
    # Using '--sdk-auth' produces better output but not available for reset
    command: List[str] = ["az", "ad", "sp", "create", f"--id={obj_id}"]
    sh.print_command(command)
    (stdout, stderr, rc) = sh.run_subprocess(command)
    sh.log_subprocess(LOG, stdout, stderr, rc, debug=ARGS.debug)
    if rc == 0 and stdout:
        service_principal = ServicePrincipal(stdout, sp_name)
        return service_principal
    else:
        return ServicePrincipal()


# https://docs.microsoft.com/en-us/cli/azure/ad/sp#az_ad_sp_create_for_rbac
# https://docs.microsoft.com/en-us/cli/azure/ad/sp/credential#az-ad-sp-credential-reset
# az ad sp create-for-rbac --name {service-principal} --skip-assignment --sdk-auth > ~/.local/local-sp.json
def service_principal_rbac_set(key_vault: str, sp_name: str, reset: bool = False) -> ServicePrincipal:
    """Method that sets Azure service principal RBAC"""
    # Using '--sdk-auth' produces better output but not available for reset
    command: List[str] = ["az", "ad", "sp"]
    if not reset:
        command.append("create-for-rbac")
    else:
        command.append("credential")
        command.append("reset")
    command.append(f"--name=http://{sp_name}")
    if not reset:
        command.append("--skip-assignment")
    sh.print_command(command)
    (stdout, stderr, rc) = sh.run_subprocess(command)
    sh.log_subprocess(LOG, stdout, stderr, rc, debug=ARGS.debug)
    if rc == 0 and stdout:
        sp_action = "reset" if reset else "created"
        LOG.info(f"successfully {sp_action} service principal credentials!")
        service_principal = ServicePrincipal(stdout, sp_name)
        return service_principal
    else:
        return ServicePrincipal()


# # https://docs.microsoft.com/en-us/cli/azure/ad/sp#az_ad_sp_create_for_rbac
# # az ad sp create-for-rbac --name ServicePrincipalName --create-cert --cert CertName --keyvault VaultName
# def service_principal_rbac_set_certificate(cert, key_vault):
#     command = ["az", "ad", "sp", "create-for-rbac"]
#     command.append("--name=http://{cert}"))
#     command.append("--create-cert")
#     command.append("--cert={cert}")
#     command.append("--keyvault={key_vault}")
#     sh.print_command(command)
#     (stdout, stderr, rc) = sh.run_subprocess(command)
#     # sh.log_subprocess(LOG, stdout, stderr, rc, debug=ARGS.debug)
#     service_principal = sh.from_json(stdout)
#     # LOG.debug("service_principal: {service_principal}")
#     # Same output as key vault secret
#     return service_principal


# def service_principal_save(path: str, service_principal: ServicePrincipal):
#     # Handle previous service principal if found
#     if sh.path_exists(path, "f"): backup_path = sh.backup_file(path)
#     # https://stackoverflow.com/questions/39491420/python-jsonexpecting-property-name-enclosed-in-double-quotes
#     # Valid JSON syntax uses quotation marks; single quotes only valid in string
#     # https://stackoverflow.com/questions/43509448/building-json-file-out-of-python-objects
#     LOG.info("storing service principal credentials...")
#     file_ready = json.dumps(service_principal.__dict__, indent=4)
#     sh.file_write(path, file_ready)
#     LOG.info("successfully saved service principal credentials!")


def service_principal_save(path: str, service_principal: ServicePrincipal):
    """Method that saves Azure service principal to a file"""
    LOG.info("storing service principal credentials...")
    sh.save_json(path, str(service_principal.__dict__))
    LOG.info("successfully saved service principal credentials!")


# --- Resource Group Commands ---
# https://docs.microsoft.com/en-us/cli/azure/group
# * Identical output for [resource_group_get, resource_group_set]

def resource_group_get(name: str) -> ResourceGroup:
    """Method that fetches Azure resource group"""
    command: List[str] = ["az", "group", "show", f"--name={name}"]
    sh.print_command(command)
    (stdout, stderr, rc) = sh.run_subprocess(command)
    # sh.log_subprocess(LOG, stdout, stderr, rc, debug=ARGS.debug)
    resource_group = ResourceGroup(stdout)
    # LOG.debug("resource_group: {resource_group}")
    return resource_group


def resource_group_set(name: str, location: str) -> ResourceGroup:
    """Method that sets Azure resource group"""
    command: List[str] = ["az", "group", "create", f"--name={name}", f"--location={location}"]
    sh.print_command(command)
    (stdout, stderr, rc) = sh.run_subprocess(command)
    # sh.log_subprocess(LOG, stdout, stderr, rc, debug=ARGS.debug)
    resource_group = ResourceGroup(stdout)
    # LOG.debug("resource_group: {resource_group}")
    return resource_group


# --- Key Vault Commands ---
# https://docs.microsoft.com/en-us/cli/azure/keyvault

def key_vault_get(resource_group: str, key_vault: str):
    """Method that fetches Azure key vault"""
    command: List[str] = ["az", "keyvault", "show",
                          f"--name={key_vault}", f"--resource-group={resource_group}"]
    sh.print_command(command)
    (stdout, stderr, rc) = sh.run_subprocess(command)
    # sh.log_subprocess(LOG, stdout, stderr, rc, debug=ARGS.debug)
    results = sh.from_json(stdout)
    # LOG.debug("results: {results}")
    return results


# Create a hardened container (vault) in Azure
def key_vault_set(resource_group: str, key_vault: str):
    """Method that sets Azure key vault"""
    command: List[str] = ["az", "keyvault", "create",
                          f"--name={key_vault}", f"--resource-group={resource_group}"]
    sh.print_command(command)
    (stdout, stderr, rc) = sh.run_subprocess(command)
    # sh.log_subprocess(LOG, stdout, stderr, rc, debug=ARGS.debug)
    results = sh.from_json(stdout)
    # LOG.debug("results: {results}")
    return results


# --- Key Vault Secret Commands ---
# https://docs.microsoft.com/en-us/cli/azure/keyvault/secret

def key_vault_secret_get(key_vault: str, secret_key: str):
    """Method that fetches Azure key vault secret"""
    command: List[str] = ["az", "keyvault", "secret", "show",
                          f"--vault-name={key_vault}", f"--name={secret_key}"]
    sh.print_command(command)
    (stdout, stderr, rc) = sh.run_subprocess(command)
    # sh.log_subprocess(LOG, stdout, stderr, rc, debug=ARGS.debug)
    if rc != 0:
        return ""
    results = sh.from_json(stdout)
    # LOG.debug("results: {results}")
    return results


def key_vault_secret_set(key_vault: str, secret_key: str, secret_value: str):
    """Method that sets Azure key vault secret"""
    LOG.info("storing key vault secret...")
    command: List[str] = ["az", "keyvault", "secret", "set",
                          f"--vault-name={key_vault}", f"--name={secret_key}", f"--value={secret_value}"]

    # command_str = str.join(" ", command)
    # command_str = command_str.split("--value=", 1)
    # command_str = "{command_str[0]}--value=*" # password hidden from log
    # LOG.debug("command => {command_str}")

    # Print password-safe version of command
    sh.print_command(command, "--value=")
    (stdout, stderr, rc) = sh.run_subprocess(command)
    # sh.log_subprocess(LOG, stdout, stderr, rc, debug=ARGS.debug)
    if rc != 0:
        return ""
    results = sh.from_json(stdout)
    # LOG.debug("results: {results}")
    return results


# https://github.com/MicrosoftDocs/azure-docs/issues/14761
# https://github.com/Azure/azure-cli/issues/7489
# az keyvault secret download --file <mySecretCert.pem> --encoding base64 --name --vault-name
# openssl pkcs12 -in <mySecretCert.pem> -out <mycert.pem> -nodes -passout
def key_vault_secret_download(cert_path: str, key_vault: str, secret_key: str) -> bool:
    """Method that downloads Azure key vault secret"""
    base_cert_path = sh.path_basename(cert_path)
    temp_cert_path: str = sh.join_path(sh.path_dir(cert_path), f"temp-{base_cert_path}")
    backup_path: str = ""
    # Handle previous certification files if found
    if sh.path_exists(temp_cert_path, "f"):
        sh.delete_file(temp_cert_path)
    if sh.path_exists(cert_path, "f"):
        backup_path = sh.backup_file(cert_path)

    # Download secret from key vault
    command: List[str] = ["az", "keyvault", "secret", "download",
                          f"--file={temp_cert_path}", "--encoding=base64",
                          f"--vault-name={key_vault}", f"--name={secret_key}"]
    sh.print_command(command)
    (stdout, stderr, rc) = sh.run_subprocess(command)
    sh.log_subprocess(LOG, stdout, stderr, rc, debug=ARGS.debug)
    if rc != 0:
        return False
    # Convert to proper format using OpenSSL
    # https://www.openssl.org/docs/man1.1.1/man1/openssl.html
    # command: List[str] = ["openssl", "pkcs12", f"-in={temp_cert_path}", f"-out={cert_path}", "-passout"]
    command: List[str] = ["openssl", "pkcs12",
                          f"-in={temp_cert_path}", f"-out={cert_path}", "-nodes", "-password pass:''"]
    sh.print_command(command)
    (stdout, stderr, rc) = sh.run_subprocess(command)
    sh.log_subprocess(LOG, stdout, stderr, rc, debug=ARGS.debug)

    # Remove recent backup if hash matches downloaded secret
    if backup_path:
        match = sh.match_file(cert_path, backup_path)
        if match:
            sh.delete_file(backup_path)

    return rc == 0


# --- Active Directory Application Commands ---
# https://docs.microsoft.com/en-us/cli/azure/ad/app

def active_directory_application_get(app_name: str) -> ActiveDirectoryApplication:
    """Method that fetches Azure Active Directory application"""
    command: List[str] = ["az", "ad", "app", "list", f"--query=[?displayName=='{app_name}'] | [0]"]
    sh.print_command(command)
    (stdout, stderr, rc) = sh.run_subprocess(command)
    # sh.log_subprocess(LOG, stdout, stderr, rc, debug=ARGS.debug)
    ad_app = ActiveDirectoryApplication(stdout)
    LOG.debug(f"ad_app: {ad_app}")
    return ad_app


def active_directory_application_set(tenant: str, app_name: str, app_id: str = "") -> ActiveDirectoryApplication:
    """Method that sets Azure Active Directory application"""
    az_ad_domain: str = f"https://{tenant}.onmicrosoft.com"
    az_ad_identifier_url: str = f"{az_ad_domain}/{app_name}"
    app_domain: str = "https://localhost:5001"
    az_ad_reply_url: str = f"{app_domain}/signin-oidc"

    if app_id:
        LOG.info("updating Azure AD application object registration...")
        command = ["az", "ad", "app", "update", f"--id={app_id}"]
    else:
        LOG.info("creating Azure AD application object registration...")
        command = ["az", "ad", "app", "create"]

    # --display-name {{az_app_registration}}
    # --homepage {{app_domain}}
    # --identifier-uris {{az_ad_identifier_urls | join(' ')}}
    # --reply-urls {{az_ad_reply_urls | join(' ')}}
    # --available-to-other-tenants {{app_authentication == 'MultiOrg'}}
    # # --required-resource-accesses {{az_ad_app_permissions | to_json}}
    # # --oauth2-allow-implicit-flow true
    # # TODO: add --app-roles once authentication testing is further
    command.extend([
        f"--display-name={app_name}",
        f"--homepage={app_domain}",
        f"--identifier-uris={az_ad_identifier_url}",
        f"--reply-urls={az_ad_reply_url}",
        "--available-to-other-tenants=true"
    ])
    sh.print_command(command)
    (stdout, stderr, rc) = sh.run_subprocess(command)
    # sh.log_subprocess(LOG, stdout, stderr, rc, debug=ARGS.debug)
    ad_app = ActiveDirectoryApplication(stdout)
    LOG.debug(f"ad_app: {ad_app}")
    return ad_app


# --- Deployment Group Commands ---
# https://docs.microsoft.com/en-us/cli/azure/deployment/group

def deployment_group_valid(rg_name: str, template_path: str, parameters: Optional[List[str]] = None, deploy_name: str = "Main") -> bool:
    """Method that validates Azure deployment group"""
    if parameters is None:
        parameters = []
    command: List[str] = ["az", "deployment", "group", "validate",
                          f"--name={deploy_name}",
                          f"--resource-group={rg_name}",
                          f"--template-file={template_path}",
                          # f"--parameters={parameters}",
                          ]
    if parameters:
        command.append("--parameters")
        command.extend(parameters)
    sh.print_command(command)
    (stdout, stderr, rc) = sh.run_subprocess(command)
    # sh.log_subprocess(LOG, stdout, stderr, rc, debug=ARGS.debug)
    return rc == 0


def deployment_group_get(rg_name: str, template_path: str, parameters: Optional[List[str]] = None, deploy_name: str = "Main") -> bool:
    """Method that fetches Azure deployment group"""
    if parameters is None:
        parameters = []
    command: List[str] = ["az", "deployment", "group", "show",
                          f"--name={deploy_name}",
                          f"--resource-group={rg_name}",
                          f"--template-file={template_path}",
                          # f"--parameters={parameters}",
                          ]
    if parameters:
        command.append("--parameters")
        command.extend(parameters)
    sh.print_command(command)
    (stdout, stderr, rc) = sh.run_subprocess(command)
    sh.log_subprocess(LOG, stdout, stderr, rc, debug=ARGS.debug)
    return rc == 0


def deployment_group_set(rg_name: str, template_path: str, parameters: Optional[List[str]] = None, deploy_name: str = "Main") -> bool:
    """Method that sets Azure deployment group"""
    if parameters is None:
        parameters = []
    command: List[str] = ["az", "deployment", "group", "create",
                          f"--name={deploy_name}",
                          f"--resource-group={rg_name}",
                          f"--template-file={template_path}"
                          # f"--parameters={parameters}"
                          ]
    if parameters:
        command.append("--parameters")
        command.extend(parameters)
    sh.print_command(command)
    (stdout, stderr, rc) = sh.run_subprocess(command)
    # sh.log_subprocess(LOG, stdout, stderr, rc, debug=ARGS.debug)
    return rc == 0


# # Certificate method ended up more trouble with no gain compared to letting service principal make its own passphrase
# # Using certificate is viable but still need to fix 'openssl' conversion in 'key_vault_secret_download'
# # - certificate results in 2 secrets (certificate, passphrase) while username/passphrase has 1
# def login_strategy_certificate(subscription: str, cert_path, tenant, key_vault):
#     cert_path = sh.expand_path(cert_path)
#     secret_key = format_resource(sh.path_filename(cert_path))
#     # Check if account subscription exists
#     LOG.debug("checking if already signed-in...")
#     account_info = account_get(subscription)

#     if not account_info:
#         if cert_path and tenant and sh.path_exists(cert_path, "f"):
#             LOG.debug("not signed-in, attempting login with certificate...")
#             account_info = account_login(secret_key, cert_path, tenant)
#             if not account_info:
#                 LOG.error("Azure certificate login failed, exiting...")
#                 sh.backup_file(cert_path)
#                 login_strategy(subscription, cert_path, tenant, key_vault)
#         else:
#             # Calling 'az login' in script works but prompt caused display issues within subprocess
#             LOG.error("not signed-in, enter 'az login' to manually login before repeating your previous command")
#             sh.fail_process()

#     # Second parse attempt; last chance to be signed-in
#     if account_info:
#         LOG.debug("signed-in, gathering account info...")
#         _account_parse(account_info)
#     else:
#         LOG.error("Azure login failed, exiting...")
#         sh.fail_process()

#     # Ensure subscription is currently active
#     if not AZ.subscription_is_default:
#         LOG.debug("activating the selected subscription...")
#         account_active = account_set(subscription)
#         if not account_active:
#             LOG.error("failed to activate subscription")
#             sh.fail_process()

#     # Ensure local certificate file exists
#     if not sh.path_exists(cert_path, "f"):
#         LOG.debug("checking key vault for certificate...")
#         # key_vault_secret = key_vault_secret_get(key_vault, secret_key)
#         # if key_vault_secret: certificate = key_vault_secret.value
#         key_vault_secret_download(cert_path, key_vault, secret_key)

#         # if certificate:
#         if sh.path_exists(cert_path, "f"):
#             LOG.debug("certificate successfully found in key vault!")
#             # LOG.debug(f"certificate: {certificate}")
#         else:
#             LOG.error("creating certificate and storing in key vault...")
#             cert_created = service_principal_rbac_set(secret_key, key_vault)
#             if cert_created:
#                 LOG.info("certificate successfully created in key vault!")
#                 # certificate = key_vault_secret_get(key_vault, secret_key)

#                 # key_vault_secret = key_vault_secret_get(key_vault, secret_key)
#                 # if key_vault_secret: certificate = key_vault_secret.value
#                 key_vault_secret_download(cert_path, key_vault, secret_key)
#             else:
#                 LOG.error("failed to create certificate")
#                 sh.fail_process()

#         # if certificate:
#         if sh.path_exists(cert_path, "f"):
#             # LOG.debug("creating local certificate...")
#             # # Create PEM file from key vault secret and pass to next login
#             # sh.file_write(cert_path, certificate)
#             LOG.info("local certificate successfully created!")
#             # Logout and confirm login with certificate file method
#             LOG.debug("logging out and attempting login with certificate...")
#             account_logout()
#             # account_info = account_login(secret_key, cert_path, tenant)
#             # if not account_info:
#             #     LOG.error("Azure certificate login failed, exiting...")
#             #     current_time = time.strftime("%Y%m%d-%H%M%S")
#             #     sh.file_rename(cert_path, f"{cert_path}.{current_time}.bak")
#             #     sh.fail_process()
#             login_strategy(subscription, cert_path, tenant, key_vault)
#         else:
#             LOG.error("failed to get certificate from key vault")
#             sh.fail_process()

#     LOG.debug("login strategy successful!")
#     LOG.debug("account_info: {account_info}")
#     return account_info


# ------------------------ Main Program ------------------------
# Initialize the logger
BASENAME = "azure_boilerplate"
ARGS: argparse.Namespace = argparse.Namespace()  # for external modules
LOG: log.Logger = log.get_logger(BASENAME)

if __name__ == "__main__":
    # Returns argparse.Namespace; to pass into function, use **vars(self.ARGS)
    def parse_arguments():
        """Method that parses arguments provided"""
        parser = argparse.ArgumentParser()
        parser.add_argument("--debug", action="store_true")
        parser.add_argument("--log-path", default="")
        return parser.parse_args()
    ARGS = parse_arguments()

    #  Configure the main logger
    LOG_HANDLERS: List[log.LogHandlerOptions] = log.default_handlers(ARGS.debug, ARGS.log_path)
    log.set_handlers(LOG, LOG_HANDLERS)
    if ARGS.debug:
        # Configure the shell_boilerplate logger
        _sh_log = log.get_logger("shell_boilerplate")
        log.set_handlers(_sh_log, LOG_HANDLERS)
        sh.ARGS.debug = ARGS.debug

    LOG.debug(f"ARGS: {ARGS}")
    LOG.debug("------------------------------------------------")

    # --- Usage Example ---
    # python ~/.local/lib/python2.7/site-packages/azure_boilerplate.py --debug
    # python ~/.local/lib/python3.6/site-packages/azure_boilerplate.py --debug
    # py $Env:AppData\Python\Python311\site-packages\boilerplates\azure_boilerplate.py --debug
