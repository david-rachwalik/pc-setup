#!/usr/bin/env python

# Basename: azure_boilerplate
# Description: Common business logic for Azure resources
# Version: 0.1.1
# VersionDate: 15 Sep 2020

# --- Global Azure Methods ---
# Helpers:                      json_parse
# authentication:               account_get, account_list, account_login
# devops authentication:        devops_login, devops_config
# service principal:            sp_create
# resource group:               resource_group_set, rg_delete
# key vault:                    kv_set, kv_get
# key vault secret:             secret_set, secret_get
# webapp service:               app_set, app_get
# app service plan:             plan_set, plan_get
# resource manager:             rm_set, rm_get
# pipelines:                    pipeline_set, pipeline_get
# SQL database:                 sql_db_set, sql_db_get

from logging_boilerplate import *
import shell_boilerplate as sh
import json

try:
    # Python 2 has both 'str' (bytes) and 'unicode' text
    basestring = basestring
    unicode = unicode
except NameError:
    # Python 3 names the unicode data type 'str'
    basestring = str
    unicode = str

# ------------------------ Classes ------------------------

class AzureGlobals(object):
    def __init__(self, tenant_id="", account="", subscription="", subscription_id="",
        subscription_is_default=False, resource_group="", location="", key_vault=""
    ):
        self.tenant_id = str(tenant_id) # active directory
        self.account = str(account) # Microsoft account (*@outlook.com, *@hotmail.com)
        self.subscription = str(subscription)
        self.subscription_id = str(subscription_id)
        self.subscription_is_default = bool(subscription_is_default)
        
        self.resource_group = str(resource_group)
        self.location = str(location)

        self.key_vault = str(key_vault)
        
        # self.client_id = str(client_id)

    def __repr__(self):
        # return self
        return vars(self)

    def __str__(self):
        # return str(self)
        return str(vars(self))


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


# ------------------------ Global Methods ------------------------

# --- Helpers ---

# https://realpython.com/python-json
def _decode_dict(dct):
    return _dict2obj(dct)


# Deserialize JSON data: https://docs.python.org/2/library/json.html
def json_parse(raw_string):
    if len(raw_string) == 0: return ""
    results = json.loads(raw_string, object_hook=_decode_dict)
    return results



# --- Account/Subscription Commands ---
# https://docs.microsoft.com/en-us/cli/azure/account

def _account_parse(obj):
    # _log.debug("Init")
    # _log.debug("obj: {0}".format(obj))

    _az.tenant_id = obj.tenantId
    # _log.debug("tenant id: {0}".format(_az.tenant_id))
    _az.account = obj.user.name
    # _log.debug("account: {0}".format(_az.account))
    _az.subscription = obj.name
    # _log.debug("subscription: {0}".format(_az.subscription))
    _az.subscription_id = obj.id
    # _log.debug("subscription id: {0}".format(_az.subscription_id))
    _az.subscription_is_default = obj.isDefault
    # _log.debug("subscription is default: {0}".format(_az.subscription_is_default))

    # _az.client_id = obj.id
    # _log.debug("subscription id: {0}".format(_az.client_id))

    _log.debug("_az: {0}".format(_az))


def account_get(subscription="Pay-As-You-Go"):
    # _log.debug("Init")
    command = ["az", "account", "show", "--subscription={0}".format(subscription)]
    _log.debug("command => {0}".format(str.join(" ", command)))
    (stdout, stderr, rc) = sh.subprocess_run(command)
    # sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
    results = json_parse(stdout)
    # _log.debug("results: {0}".format(results))
    return results


def account_list():
    # _log.debug("Init")
    command = ["az", "account", "list", "--all"]
    _log.debug("command => {0}".format(str.join(" ", command)))
    (stdout, stderr, rc) = sh.subprocess_run(command)
    # sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
    results = json_parse(stdout)
    # _log.debug("results: {0}".format(results))
    return results


def account_set(subscription="Pay-As-You-Go"):
    # _log.debug("Init")
    command = ["az", "account", "set", "--subscription={0}".format(subscription)]
    _log.debug("command => {0}".format(str.join(" ", command)))
    (stdout, stderr, rc) = sh.subprocess_run(command)
    # sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
    return (rc == 0)


def account_login(prompt=True):
    # _log.debug("Init")

    # Check if account subscription exists
    _log.debug("check if already signed-in...")
    account_info = account_get()
    _log.debug("account_info: {0}".format(account_info))

    if account_info:
        _log.debug("signed-in, gathering account info...")
        _account_parse(account_info)
    else:
        # Prompt manual login if not signed-in
        _log.error("account subscription doesn't exist, exiting...")
        sh.process_fail()
        # _log.debug("account not signed-in, logging in now...")
    
    # Ensure subscription is currently active
    if not _az.subscription_is_default:
        _log.debug("activating subscription...")
        account_active = account_set()
        if not account_active:
            _log.error("failed to activate subscription")
            sh.process_fail()


    # if account_info:
    #     _log.debug("signed-in, gathering account info...")
    # else:
    if not account_info:
        _log.debug("prompt: {0}".format(prompt))
        if prompt:
            _log.debug(":: mock prompt for manual sign-in ::")
        else:
            # Only expect to reach here when --quiet is flagged
            _log.debug("not signed-in, exiting...")
            sh.process_fail()

    return account_info


# --- Resource Group Commands ---
# https://docs.microsoft.com/en-us/cli/azure/group
# * Identical output for [resource_group_get, resource_group_set]

def _resource_group_parse(obj):
    # _log.debug("Init")
    # _log.debug("obj: {0}".format(obj))

    _az.resource_group = obj.name
    _az.location = obj.location
    
    _log.debug("_az: {0}".format(_az))


def resource_group_get(name=""):
    # _log.debug("Init")
    command = ["az", "group", "show", "--name={0}".format(name)]
    _log.debug("command => {0}".format(str.join(" ", command)))
    (stdout, stderr, rc) = sh.subprocess_run(command)
    # sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
    results = json_parse(stdout)
    # _log.debug("results: {0}".format(results))
    return results


def resource_group_set(name="", location=""):
    # _log.debug("Init")
    rg_info = resource_group_get(name)
    # _log.debug("rg_info: {0}".format(rg_info))

    if rg_info:
        _log.debug("resource group exists, gathering info...")
        # return True
    else:
        # Prompt manual login if not signed-in
        _log.error("resource group doesn't exists, creating...")
        command = ["az", "group", "create", "--name={0}".format(name), "--location={0}".format(location)]
        _log.debug("command => {0}".format(str.join(" ", command)))
        (stdout, stderr, rc) = sh.subprocess_run(command)
        # sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
        rg_info = json_parse(stdout)
        # _log.debug("rg_info: {0}".format(rg_info))
        # return (rc == 0)
    
    _resource_group_parse(rg_info)
    return rg_info


# --- Key Vault Commands ---
# https://docs.microsoft.com/en-us/cli/azure/keyvault

def _key_vault_parse(obj):
    # _log.debug("Init")
    # _log.debug("obj: {0}".format(obj))

    _az.tenant_id = obj.properties.tenantId
    _az.key_vault = obj.name
    _az.resource_group = obj.resourceGroup
    _az.location = obj.location
    
    _log.debug("_az: {0}".format(_az))


def key_vault_get(name="", resource_group=""):
    # _log.debug("Init")
    command = ["az", "keyvault", "show", "--name={0}".format(name), "--resource-group={0}".format(resource_group)]
    _log.debug("command => {0}".format(str.join(" ", command)))
    (stdout, stderr, rc) = sh.subprocess_run(command)
    # sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
    results = json_parse(stdout)
    # _log.debug("results: {0}".format(results))
    return results


def key_vault_set(name="", resource_group=""):
    # _log.debug("Init")
    key_vault_info = key_vault_get(name)
    # _log.debug("key_vault_info: {0}".format(key_vault_info))

    if key_vault_info:
        _log.debug("key vault exists, gathering info...")
        # return True
    else:
        # Prompt manual login if not signed-in
        _log.error("key vault doesn't exists, creating...")
        command = ["az", "keyvault", "create", "--name={0}".format(name), "--location={0}".format(location)]
        _log.debug("command => {0}".format(str.join(" ", command)))
        (stdout, stderr, rc) = sh.subprocess_run(command)
        # sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
        key_vault_info = json_parse(stdout)
        # _log.debug("key_vault_info: {0}".format(key_vault_info))
        # return (rc == 0)
    
    _key_vault_parse(key_vault_info)
    return key_vault_info


# --- Key Vault Secret Commands ---
# https://docs.microsoft.com/en-us/cli/azure/keyvault/secret

def _key_vault_secret_parse(obj):
    # _log.debug("Init")
    # _log.debug("obj: {0}".format(obj))

    _az.secret_key = obj.name
    _az.secret_value = obj.value
    
    _log.debug("_az: {0}".format(_az))


def key_vault_secret_get(key_vault="", secret_key=""):
    # _log.debug("Init")
    command = ["az", "keyvault", "secret", "show", "--vault-name={0}".format(key_vault), "--name={0}".format(secret_key)]
    _log.debug("command => {0}".format(str.join(" ", command)))
    (stdout, stderr, rc) = sh.subprocess_run(command)
    # sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
    results = json_parse(stdout)
    # _log.debug("results: {0}".format(results))
    return results


def key_vault_secret_set(key_vault="", secret_key="", secret_value=""):
    # _log.debug("Init")
    key_vault_secret_info = key_vault_secret_get(key_vault, secret_key)
    # _log.debug("key_vault_secret_info: {0}".format(key_vault_secret_info))

    if key_vault_secret_info:
        _log.debug("key vault secret exists, gathering info...")
        # return True
    else:
        # Prompt manual login if not signed-in
        _log.error("key vault secret doesn't exists, creating...")
        command = ["az", "keyvault", "secret", "set", "--vault-name={0}".format(key_vault), "--name={0}".format(secret_key), "--value={0}".format(secret_value)]
        _log.debug("command => {0}".format(str.join(" ", command)))
        (stdout, stderr, rc) = sh.subprocess_run(command)
        # sh.subprocess_log(_log, stdout, stderr, rc, debug=args.debug)
        key_vault_secret_info = json_parse(stdout)
        # _log.debug("key_vault_secret_info: {0}".format(key_vault_secret_info))
        # return (rc == 0)
    
    _key_vault_secret_parse(key_vault_secret_info)
    return key_vault_secret_info


# ------------------------ Main Program ------------------------

# Initialize the logger
basename = "azure_boilerplate"
args = LogArgs() # for external modules
log_options = LogOptions(basename)
_log = get_logger(log_options)
_az = AzureGlobals()

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
