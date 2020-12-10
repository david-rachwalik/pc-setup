#!/usr/bin/env python

# Basename: azure_boilerplate
# Description: Common business logic for Azure resources
# Version: 0.1.1
# VersionDate: 15 Sep 2020

# --- Global Azure Classes ---
# Account:                      is_signed_in, tenant_id, account_user, subscription, subscription_id, subscription_is_default
# ServicePrincipal:             name, appId, password

# --- Global Azure Methods ---
# :-Helper-:                    json_parse, format_resource, get_random_password
# account:                      account_get, account_list, account_logout, account_login, account_set
# service principal:            service_principal_get, service_principal_rbac_set, service_principal_save
# resource group:               resource_group_get, resource_group_set, resource_group_delete
# key vault:                    key_vault_get, key_vault_set
# key vault secret:             key_vault_secret_get, key_vault_secret_set, key_vault_secret_download
# active directory:             active_directory_application_get, active_directory_application_set



# TODO:
# devops authentication:        devops_login, devops_config
# webapp service:               app_set, app_get
# app service plan:             plan_set, plan_get
# resource manager:             rm_set, rm_get
# pipelines:                    pipeline_set, pipeline_get
# SQL database:                 sql_db_set, sql_db_get


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

# ------------------------ Classes ------------------------

# https://goodcode.io/articles/python-dict-object
# Access dictionary items as object attributes
class _dict2obj(dict):
    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError("No such attribute: " + name)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            raise AttributeError("No such attribute: " + name)


class AzureBase(object):
    def __repr__(self):
        return vars(self)

    def __str__(self):
        return str(vars(self))


class Account(AzureBase):
    def __init__(self, obj=""):
        self.tenant_id = "" # active directory
        self.account_user = "" # Microsoft account (*@outlook.com, *@hotmail.com)
        self.subscription = ""
        self.subscription_id = ""
        self.subscription_is_default = False
        self.is_signed_in = False

        # Business logic for parsing
        if obj and isinstance(obj, str): obj = json_parse(obj)
        # Sometimes the output is a list (e.g. 'az login')
        # TODO: search by subscription name instead of always first result
        if obj and isinstance(obj, list): obj = obj[0]
        if isinstance(obj, _dict2obj):
            self.tenant_id = obj.tenantId
            self.account_user = obj.user.name
            self.subscription = obj.name
            self.subscription_id = obj.id
            self.subscription_is_default = obj.isDefault
            self.is_signed_in = bool(self.tenant_id and self.subscription_id)


# Attribute names match stdout for consistent JSON serialization
class ServicePrincipal(AzureBase):
    def __init__(self, obj="", sp_name=""):
        self.name = sp_name
        self.appId = ""
        self.password = ""

        # Business logic for parsing
        if obj and isinstance(obj, str): obj = json_parse(obj)
        if isinstance(obj, _dict2obj):
            keys = obj.keys()

            # keys for 'az ad sp show', 'az ad sp create-for-rbac', 'az ad sp credential reset'
            # - [name, appId,    password,     tenant]
            # keys for 'az ad sp create-for-rbac --sdk-auth'
            # - [      clientId, clientSecret, tenantId]

            if ("name" in keys): self.name = sh.path_basename(obj.name)
            if ("appId" in keys): self.appId = obj.appId
            if ("password" in keys): self.password = obj.password


class ResourceGroup(AzureBase):
    def __init__(self, obj=""):
        self.location = ""
        self.name = ""

        # Business logic for parsing
        if obj and isinstance(obj, str): obj = json_parse(obj)
        if isinstance(obj, _dict2obj):
            self.location = obj.location
            self.name = obj.name
            self.is_valid = bool(self.location and self.name)


class ActiveDirectoryApplication(AzureBase):
    def __init__(self, obj=""):
        self.appId = "" # client_id

        # Business logic for parsing
        if obj and isinstance(obj, str): obj = json_parse(obj)
        if isinstance(obj, _dict2obj):
            self.appId = obj.appId



# ------------------------ Global Methods ------------------------

# --- Helper Commands ---

# https://realpython.com/python-json
def _decode_dict(dct):
    return _dict2obj(dct)


# Deserialize JSON data: https://docs.python.org/2/library/json.html
def json_parse(raw_string):
    if not raw_string: return ""
    results = json.loads(raw_string, object_hook=_decode_dict)
    return results


# Must conform to the following pattern: '^[0-9a-zA-Z-]+$'
def format_resource(raw_name):
    name = re.sub('[^a-zA-Z0-9 \n\.]', '-', raw_name)
    # _log.debug("name: {0}".format(name))
    return name


# https://pynative.com/python-generate-random-string
def get_random_password(length=16):
    import random, string
    # Load all lower/upper case letters, digits, and special characters
    random_source = string.ascii_letters + string.digits + string.punctuation
    # Guarantee at least 1 of each
    password = random.choice(string.ascii_lowercase)
    password += random.choice(string.ascii_uppercase)
    password += random.choice(string.digits)
    password += random.choice(string.punctuation)
    # Fill in the remaining length
    for i in range(length - 4):
        password += random.choice(random_source)
    # Randomly shuffle all the characters
    password_list = list(password)
    random.SystemRandom().shuffle(password_list)
    password = "".join(password_list)
    return password



# --- Account/Subscription Commands ---
# https://docs.microsoft.com/en-us/cli/azure/account

def account_get(subscription):
    if not (subscription and isinstance(subscription, str)): TypeError("'subscription' parameter expected as string")
    command = ["az", "account", "show", "--subscription={0}".format(subscription)]
    sh.print_command(command)
    (stdout, stderr, rc) = sh.subprocess_run(command)
    # sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
    if (rc != 0): return Account()
    # Return the parsed account data
    results = Account(stdout)
    # _log.debug("results: {0}".format(results))
    return results


def account_list():
    command = ["az", "account", "list", "--all"]
    sh.print_command(command)
    (stdout, stderr, rc) = sh.subprocess_run(command)
    # sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
    if (rc != 0): return Account()
    # Return the parsed account data
    results = Account(stdout)
    # _log.debug("results: {0}".format(results))
    return results


def account_logout():
    command = ["az", "logout"]
    sh.print_command(command)
    (stdout, stderr, rc) = sh.subprocess_run(command)
    # sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
    return (rc == 0)


# https://docs.microsoft.com/en-us/cli/azure/reference-index#az_login
# Login with username (service principal) and password (client secret/certificate)
def account_login(organization="", name="", password=""):
    command = ["az", "login"]
    # az login --service-principal -u <app-url> -p <password-or-cert> --tenant <tenant>
    if organization and name and password:
        command.append("--service-principal")
        command.append("--tenant={0}.onmicrosoft.com".format(organization))
        command.append("--username=http://{0}".format(name))
        command.append("--password={0}".format(password))
        command.append("--allow-no-subscriptions")
    # Print password-safe version of command
    sh.print_command(command, "--password=")
    (stdout, stderr, rc) = sh.subprocess_run(command)
    # sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
    if (rc != 0): return Account()
    # Return the parsed account data
    results = Account(stdout)
    # _log.debug("results: {0}".format(results))
    return results


def account_set(subscription):
    if not (subscription and isinstance(subscription, str)): TypeError("'subscription' parameter expected as string")
    command = ["az", "account", "set", "--subscription={0}".format(subscription)]
    sh.print_command(command)
    (stdout, stderr, rc) = sh.subprocess_run(command)
    # sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
    return (rc == 0)



# --- Service Principal Commands ---
# https://docs.microsoft.com/en-us/cli/azure/ad/sp

# Always use service principal name (not id)
def service_principal_get(sp_name, sp_dir=""):
    if not (sp_name and isinstance(sp_name, str)): TypeError("'sp_name' parameter expected as string")
    # Full filepath to service principal data
    sp_name = format_resource(sp_name)
    sp_path = sh.path_join(sh.path_expand(sp_dir), "{0}.json".format(sp_name))
    # Gather login info from service principal
    if sp_dir:
        _log.debug("gathering service principal credentials from file...")
        stdout = sh.file_read(sp_path)
    else:
        _log.debug("gathering service principal from Azure...")
        # if not sp_name.startswith("http://"): sp_name = "http://{0}".format(sp_name)
        command = ["az", "ad", "sp", "show", "--id=http://{0}".format(sp_name)]
        sh.print_command(command)
        (stdout, stderr, rc) = sh.subprocess_run(command)
        # sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
        if (rc != 0): return None
    # Return the parsed service principal data
    # service_principal = _service_principal_parse(stdout, sp_name)
    service_principal = ServicePrincipal(stdout, sp_name)
    # _log.debug("service_principal: {0}".format(service_principal))
    return service_principal


# https://docs.microsoft.com/en-us/cli/azure/ad/sp#az_ad_sp_create_for_rbac
# https://docs.microsoft.com/en-us/cli/azure/ad/sp/credential#az-ad-sp-credential-reset
# az ad sp create-for-rbac --name {service-principal} --skip-assignment --sdk-auth > ~/.local/local-sp.json
def service_principal_rbac_set(key_vault, sp_name, reset=False):
    if not (key_vault and isinstance(key_vault, str)): TypeError("'key_vault' parameter expected as string")
    if not (sp_name and isinstance(sp_name, str)): TypeError("'sp_name' parameter expected as string")
    # Using '--sdk-auth' produces better output but not available for reset
    command = ["az", "ad", "sp"]
    if not reset:
        command.append("create-for-rbac")
    else:
        command.append("credential")
        command.append("reset")
    command.append("--name={0}".format("http://{0}".format(sp_name)))
    if not reset:
        command.append("--skip-assignment")
    sh.print_command(command)
    (stdout, stderr, rc) = sh.subprocess_run(command)
    sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
    if rc == 0 and stdout:
        _log.info("successfully {0} service principal credentials!".format("reset" if reset else "created"))
        # service_principal = _service_principal_parse(stdout, sp_name)
        service_principal = ServicePrincipal(stdout, sp_name)
        return service_principal
    else:
        return None


# # https://docs.microsoft.com/en-us/cli/azure/ad/sp#az_ad_sp_create_for_rbac
# # az ad sp create-for-rbac --name ServicePrincipalName --create-cert --cert CertName --keyvault VaultName
# def service_principal_rbac_set_certificate(cert, key_vault):
#     command = ["az", "ad", "sp", "create-for-rbac"]
#     command.append("--name={0}".format("http://{0}".format(cert)))
#     command.append("--create-cert")
#     command.append("--cert={0}".format(cert))
#     command.append("--keyvault={0}".format(key_vault))
#     sh.print_command(command)
#     (stdout, stderr, rc) = sh.subprocess_run(command)
#     # sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
#     service_principal = json_parse(stdout)
#     # _log.debug("service_principal: {0}".format(service_principal))
#     # Same output as key vault secret
#     return service_principal


def service_principal_save(path, service_principal):
    if not (path and isinstance(path, str)): TypeError("'path' parameter expected as string")
    if not isinstance(service_principal, ServicePrincipal): TypeError("'service_principal' parameter expected as ServicePrincipal")
    # Handle previous service principal if found
    if sh.path_exists(path, "f"): backup_path = sh.file_backup(path)
    # https://stackoverflow.com/questions/39491420/python-jsonexpecting-property-name-enclosed-in-double-quotes
    # Valid JSON syntax uses quotation marks; single quotes only valid in string
    # https://stackoverflow.com/questions/43509448/building-json-file-out-of-python-objects
    _log.info("storing service principal credentials...")
    file_ready = json.dumps(service_principal.__dict__, indent=4)
    sh.file_write(path, file_ready)
    _log.info("successfully saved service principal credentials!")



# --- Resource Group Commands ---
# https://docs.microsoft.com/en-us/cli/azure/group
# * Identical output for [resource_group_get, resource_group_set]

def resource_group_get(name=""):
    command = ["az", "group", "show", "--name={0}".format(name)]
    sh.print_command(command)
    (stdout, stderr, rc) = sh.subprocess_run(command)
    # sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
    resource_group = ResourceGroup(stdout)
    _log.debug("resource_group: {0}".format(resource_group))
    return resource_group


def resource_group_set(name="", location=""):
    resource_group = resource_group_get(name)
    rg_changed = False
    if not resource_group:
        _log.warning("resource group doesn't exists, creating...")
        command = ["az", "group", "create", "--name={0}".format(name), "--location={0}".format(location)]
        sh.print_command(command)
        (stdout, stderr, rc) = sh.subprocess_run(command)
        # sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
        resource_group = ResourceGroup(stdout)
        _log.debug("resource_group: {0}".format(resource_group))
        rg_changed = True
    return (resource_group, rg_changed)


# --- Key Vault Commands ---
# https://docs.microsoft.com/en-us/cli/azure/keyvault

def key_vault_get(name="", resource_group=""):
    command = ["az", "keyvault", "show", "--name={0}".format(name), "--resource-group={0}".format(resource_group)]
    sh.print_command(command)
    (stdout, stderr, rc) = sh.subprocess_run(command)
    # sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
    results = json_parse(stdout)
    # _log.debug("results: {0}".format(results))
    return results


def key_vault_set(name="", resource_group=""):
    key_vault_info = key_vault_get(name)
    # _log.debug("key_vault_info: {0}".format(key_vault_info))

    if key_vault_info:
        _log.debug("key vault exists, gathering info...")
        # TODO: parse key vault into class and return
    else:
        _log.warning("key vault doesn't exists, creating...")
        command = ["az", "keyvault", "create", "--name={0}".format(name), "--location={0}".format(location)]
        sh.print_command(command)
        (stdout, stderr, rc) = sh.subprocess_run(command)
        # sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
        key_vault_info = json_parse(stdout)
        # _log.debug("key_vault_info: {0}".format(key_vault_info))
        # return (rc == 0)
    
    return key_vault_info


# --- Key Vault Secret Commands ---
# https://docs.microsoft.com/en-us/cli/azure/keyvault/secret

def key_vault_secret_get(key_vault, secret_key):
    command = ["az", "keyvault", "secret", "show", "--vault-name={0}".format(key_vault), "--name={0}".format(secret_key)]
    sh.print_command(command)
    (stdout, stderr, rc) = sh.subprocess_run(command)
    # sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
    if (rc != 0): return ""
    results = json_parse(stdout)
    # _log.debug("results: {0}".format(results))
    return results.value


def key_vault_secret_set(key_vault, secret_key, secret_value):
    _log.info("storing key vault secret...")
    command = ["az", "keyvault", "secret", "set", "--vault-name={0}".format(key_vault), "--name={0}".format(secret_key), "--value={0}".format(secret_value)]
    
    # command_str = str.join(" ", command)
    # command_str = command_str.split("--value=", 1)
    # command_str = "{0}--value=*".format(command_str[0]) # password hidden from log
    # _log.debug("command => {0}".format(command_str))

    # Print password-safe version of command
    sh.print_command(command, "--value=")
    (stdout, stderr, rc) = sh.subprocess_run(command)
    # sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
    if (rc != 0): return ""
    results = json_parse(stdout)
    # _log.debug("results: {0}".format(results))
    return results


# https://github.com/MicrosoftDocs/azure-docs/issues/14761
# https://github.com/Azure/azure-cli/issues/7489
# az keyvault secret download --file <mySecretCert.pem> --encoding base64 --name --vault-name
# openssl pkcs12 -in <mySecretCert.pem> -out <mycert.pem> -nodes -passout
def key_vault_secret_download(cert_path, key_vault, secret_key):
    temp_cert_path = sh.path_join(sh.path_dir(cert_path), "temp-{0}".format(sh.path_basename(cert_path)))
    backup_path = ""
    # Handle previous certification files if found
    if sh.path_exists(temp_cert_path, "f"): sh.file_delete(temp_cert_path)
    if sh.path_exists(cert_path, "f"): backup_path = sh.file_backup(cert_path)
    
    # Download secret from key vault
    command = ["az", "keyvault", "secret", "download",
        "--file={0}".format(temp_cert_path), "--encoding=base64",
        "--vault-name={0}".format(key_vault), "--name={0}".format(secret_key)]
    sh.print_command(command)
    (stdout, stderr, rc) = sh.subprocess_run(command)
    sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
    if (rc != 0): return False
    # Convert to proper format using OpenSSL
    # https://www.openssl.org/docs/man1.1.1/man1/openssl.html
    # command = ["openssl", "pkcs12", "-in={0}".format(temp_cert_path), "-out={0}".format(cert_path), "-passout"]
    command = ["openssl", "pkcs12", "-in={0}".format(temp_cert_path), "-out={0}".format(cert_path), "-nodes", "-password pass:''"]
    sh.print_command(command)
    (stdout, stderr, rc) = sh.subprocess_run(command)
    sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)

    # Remove recent backup if hash matches downloaded secret
    if backup_path:
        match = sh.file_match(cert_path, backup_path)
        if match: sh.file_delete(backup_path)

    return (rc == 0)



# --- Active Directory Application Commands ---
# https://docs.microsoft.com/en-us/cli/azure/ad/app

def active_directory_application_get(app_name):
    command = ["az", "ad", "app", "list", "--query=[?displayName=='{0}'] | [0]".format(app_name)]

    sh.print_command(command)
    (stdout, stderr, rc) = sh.subprocess_run(command)
    sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
    # if (rc != 0): return None
    # results = json_parse(stdout)
    # _log.debug("results: {0}".format(results))
    # return results.value
    ad_app = ActiveDirectoryApplication(stdout)
    _log.debug("resource_group: {0}".format(resource_group))
    return ad_app


def active_directory_application_set(app_name, secret_key, secret_value):
    _log.info("storing key vault secret...")
    command = ["az", "keyvault", "secret", "set", "--vault-name={0}".format(app_name), "--name={0}".format(secret_key), "--value={0}".format(secret_value)]
    # Print password-safe version of command
    sh.print_command(command, "--value=")
    (stdout, stderr, rc) = sh.subprocess_run(command)
    sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
    if (rc != 0): return ""
    results = json_parse(stdout)
    _log.debug("results: {0}".format(results))
    return results





# # Certificate method ended up more trouble with no gain compared to letting service principal make its own passphrase
# # Using certificate is viable but still need to fix 'openssl' conversion in 'key_vault_secret_download'
# # - certificate results in 2 secrets (certificate, passphrase) while username/passphrase has 1
# def login_strategy_certificate(subscription, cert_path, tenant, key_vault):
#     if not (subscription and isinstance(subscription, str)):
#         TypeError("login_strategy() expects 'subscription' parameter as string")
#     cert_path = sh.path_expand(cert_path)
#     secret_key = format_resource(sh.path_filename(cert_path))
#     # Check if account subscription exists
#     _log.debug("checking if already signed-in...")
#     account_info = account_get(subscription)

#     if not account_info:
#         if cert_path and tenant and sh.path_exists(cert_path, "f"):
#             _log.debug("not signed-in, attempting login with certificate...")
#             account_info = account_login(secret_key, cert_path, tenant)
#             if not account_info:
#                 _log.error("Azure certificate login failed, exiting...")
#                 sh.file_backup(cert_path)
#                 login_strategy(subscription, cert_path, tenant, key_vault)
#         else:
#             # Calling 'az login' in script works but prompt caused display issues within subprocess
#             _log.error("not signed-in, enter 'az login' to manually login before repeating your previous command")
#             sh.process_fail()

#     # Second parse attempt; last chance to be signed-in
#     if account_info:
#         _log.debug("signed-in, gathering account info...")
#         _account_parse(account_info)
#     else:
#         _log.error("Azure login failed, exiting...")
#         sh.process_fail()

#     # Ensure subscription is currently active
#     if not _az.subscription_is_default:
#         _log.debug("activating the selected subscription...")
#         account_active = account_set(subscription)
#         if not account_active:
#             _log.error("failed to activate subscription")
#             sh.process_fail()

#     # Ensure local certificate file exists
#     if not sh.path_exists(cert_path, "f"):
#         _log.debug("checking key vault for certificate...")
#         # key_vault_secret = key_vault_secret_get(key_vault, secret_key)
#         # if key_vault_secret: certificate = key_vault_secret.value
#         key_vault_secret_download(cert_path, key_vault, secret_key)

#         # if certificate:
#         if sh.path_exists(cert_path, "f"):
#             _log.debug("certificate successfully found in key vault!")
#             # _log.debug("certificate: {0}".format(certificate))
#         else:
#             _log.error("creating certificate and storing in key vault...")
#             cert_created = service_principal_rbac_set(secret_key, key_vault)
#             if cert_created:
#                 _log.info("certificate successfully created in key vault!")
#                 # certificate = key_vault_secret_get(key_vault, secret_key)

#                 # key_vault_secret = key_vault_secret_get(key_vault, secret_key)
#                 # if key_vault_secret: certificate = key_vault_secret.value
#                 key_vault_secret_download(cert_path, key_vault, secret_key)
#             else:
#                 _log.error("failed to create certificate")
#                 sh.process_fail()

#         # if certificate:
#         if sh.path_exists(cert_path, "f"):
#             # _log.debug("creating local certificate...")
#             # # Create PEM file from key vault secret and pass to next login
#             # sh.file_write(cert_path, certificate)
#             _log.info("local certificate successfully created!")
#             # Logout and confirm login with certificate file method
#             _log.debug("logging out and attempting login with certificate...")
#             account_logout()
#             # account_info = account_login(secret_key, cert_path, tenant)
#             # if not account_info:
#             #     _log.error("Azure certificate login failed, exiting...")
#             #     current_time = time.strftime("%Y%m%d-%H%M%S")
#             #     sh.file_rename(cert_path, "{0}.{1}.bak".format(cert_path, current_time))
#             #     sh.process_fail()
#             login_strategy(subscription, cert_path, tenant, key_vault)
#         else:
#             _log.error("failed to get certificate from key vault")
#             sh.process_fail()

#     _log.debug("login strategy successful!")
#     _log.debug("account_info: {0}".format(account_info))
#     return account_info



# ------------------------ Main Program ------------------------

# Initialize the logger
basename = "azure_boilerplate"
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
    # python ~/.local/lib/python2.7/site-packages/azure_boilerplate.py --debug
    # python ~/.local/lib/python3.6/site-packages/azure_boilerplate.py --debug
