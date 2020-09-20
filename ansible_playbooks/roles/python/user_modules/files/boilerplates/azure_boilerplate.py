#!/usr/bin/env python

# Basename: azure_boilerplate
# Description: Common business logic for Azure resources
# Version: 0.1.1
# VersionDate: 15 Sep 2020

# --- Global Azure Methods ---
# Helpers:                      json_parse
# authentication:               account_show, account_list, account_login
# devops authentication:        devops_login, devops_config
# service principal:            sp_create
# resource group:               rg_create, rg_delete
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
        subscription_is_default=False
    ):
        self.tenant_id = str(tenant_id) # active directory
        self.account = str(account) # Microsoft account (*@outlook.com, *@hotmail.com)
        self.subscription = str(subscription)
        self.subscription_id = str(subscription_id)
        self.subscription_is_default = bool(subscription_is_default)
        
        # self.client_id = str(client_id)


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
    results = json.loads(raw_string, object_hook=_decode_dict)
    return results



# --- Account/Subscription Commands ---
# https://docs.microsoft.com/en-us/cli/azure/account

def _account_parse(obj):
    # _log.debug("(_account_parse): Init")
    _az.tenant_id = obj.tenantId
    # _log.debug("(account_login): tenant id: {0}".format(_az.tenant_id))
    _az.account = obj.user.name
    # _log.debug("(account_login): account: {0}".format(_az.account))
    _az.subscription = obj.name
    # _log.debug("(account_login): subscription: {0}".format(_az.subscription))
    _az.subscription_id = obj.id
    # _log.debug("(account_login): subscription id: {0}".format(_az.subscription_id))
    _az.subscription_is_default = obj.isDefault
    # _log.debug("(account_login): subscription is default: {0}".format(_az.subscription_is_default))

    # _az.client_id = obj.id
    # _log.debug("(account_login): subscription id: {0}".format(_az.client_id))


def account_show(subscription="Pay-As-You-Go"):
    # _log.debug("(account_show): Init")
    command = ["az", "account", "show", "--subscription={0}".format(subscription)]
    _log.debug("(account_show): command => {0}".format(str.join(" ", command)))
    (stdout, stderr, rc) = sh.subprocess_run(command)
    # sh.subprocess_log(_log, stdout, stderr, rc, prefix="account_show", debug=True)
    results = json_parse(stdout)
    # _log.debug("(account_show): results: {0}".format(results))
    return results


def account_list():
    # _log.debug("(account_list): Init")
    command = ["az", "account", "list", "--all"]
    _log.debug("(account_list): command => {0}".format(str.join(" ", command)))
    (stdout, stderr, rc) = sh.subprocess_run(command)
    # sh.subprocess_log(_log, stdout, stderr, rc, prefix="account_list", debug=True)
    results = json_parse(stdout)
    # _log.debug("(account_list): results: {0}".format(results))
    return results


def account_set(subscription="Pay-As-You-Go"):
    # _log.debug("(account_set): Init")
    command = ["az", "account", "set", "--subscription={0}".format(subscription)]
    _log.debug("(account_set): command => {0}".format(str.join(" ", command)))
    (stdout, stderr, rc) = sh.subprocess_run(command)
    # sh.subprocess_log(_log, stdout, stderr, rc, prefix="account_set", debug=True)
    return (rc == 0)


def account_login(prompt=True):
    # _log.debug("(account_login): Init")

    # Check if account subscription exists
    _log.debug("(account_login): check if already signed-in...")
    account_info = account_show()
    _log.debug("(account_login): account_info: {0}".format(account_info))

    if account_info:
        _log.debug("account is signed-in, parsing...")
        _account_parse(account_info)
    else:
        # Prompt manual login if not signed-in
        _log.debug("account not signed-in, logging in now...")

    # Ensure subscription is currently active
    if not _az.subscription_is_default:
        _log.debug("(account_login): activating subscription...")
        account_active = _az.account_set()
        if not account_active:
            _log.error("(account_login): failed to activate subscription")
            sh.process_fail()


    if account_info:
        _log.debug("(account_login): already signed-in!")
        _log.debug("(account_login): gather account info...")
    else:
        _log.debug("(account_login): prompt: {0}".format(prompt))
        if prompt:
            _log.debug("(account_login): :: mock prompt for manual sign-in ::")
        else:
            # Only expect to reach here when --quiet is flagged
            _log.debug("(account_login): not signed-in, exiting...")
            sh.process_fail()

    return account_info


# --- Account/Subscription Commands ---
# https://docs.microsoft.com/en-us/cli/azure/account

def key_vault_create():
    _log.debug("(key_vault_create): Init")


# ------------------------ Main Program ------------------------

# Initialize the logger
basename = "azure_boilerplate"
log_options = LogOptions(basename)
_log = get_logger(log_options)
_az = AzureGlobals()

if __name__ == "__main__":
    # Returns argparse.Namespace; to pass into function, use **vars(self.args)
    def parse_arguments():
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--debug", action="store_true")
        return parser.parse_args()
    args = parse_arguments()

    # Configure the main logger
    log_level = 20                  # logging.INFO
    if args.debug: log_level = 10   # logging.DEBUG
    log_stream_options = LogHandlerOptions(log_level)
    set_handlers(_log, [log_stream_options])

    _log.debug("(__main__): args: {0}".format(args))
    _log.debug("(__main__): ------------------------------------------------")


    # --- Usage Example ---
    # python ~/.local/lib/python2.7/site-packages/azure_boilerplate.py --debug
    # python ~/.local/lib/python3.6/site-packages/azure_boilerplate.py --debug
