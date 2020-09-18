#!/usr/bin/env python

# Basename: azure_boilerplate
# Description: Common business logic for Azure resources
# Version: 0.1.1
# VersionDate: 15 Sep 2020

# --- Global Azure Commands ---
# authentication:               subscription_login, service_principal_create
# devops authentication:        devops_login, devops_config
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

def subscription_login(prompt=True):
    logger.debug("(subscription_login): Init")
    logger.debug("(subscription_login): prompt: {0}".format(prompt))

    logger.debug("(subscription_login): check if already signed-in...")
    signed_in = False

    if signed_in:
        logger.debug("(subscription_login): already signed-in!")
        logger.debug("(subscription_login): gather subscription info...")
    else:
        if prompt:
            logger.debug("(subscription_login): :: mock prompt for manual sign-in ::")
        else:
            # Only expect to reach here when --quiet is flagged
            logger.debug("(subscription_login): not signed-in, exiting...")
            sh.process_fail()

    return signed_in



# ------------------------ Main Program ------------------------

# Initialize the logger
basename = "azure_boilerplate"
log_options = LogOptions(basename)
logger = get_logger(log_options)

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
    logger.setLevel(log_level)
    
    logger.debug("(__main__): args: {0}".format(args))
    logger.debug("(__main__): ------------------------------------------------")


    # --- Usage Example ---
    # python ~/.local/lib/python2.7/site-packages/azure_boilerplate.py --debug
