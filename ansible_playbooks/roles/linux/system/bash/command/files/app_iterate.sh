#!/bin/bash

# --- Example Usage Commands ---
# setup --tags sh
# app_iterate


# --- Script to quickly iterate upon 'app' command for development ---
cd ~/pc-setup/ansible_playbooks
ansible-playbook system_setup.yml --tags "py" --skip-tags "windows"

# --- Test Azure login (service principal) ---
# app login --debug

# --- Test creating a secret in Azure Key Vault ---
# app secret --debug --resource-group="Main" --key-vault="main-keyvault" --secret-key="AutoTestKey" --secret-value="007"

# --- Test creating an ASP.NET Core Application ---
# app client --debug --application "Tutorials-net3-1-WebApps-RazorPages" --project "RazorPagesMovie" --source "github" --framework "netcoreapp3.1"
# app client --debug --application "Tutorials-net3-1-DataAccess-RazorPages" --project "ContosoUniversity" --source "github" --framework "netcoreapp3.1" --strat "database"
# app client --debug --application "Tutorials-net5-0-WebApps-RazorPages" --project "RazorPagesMovie" --source "github"
# app client --debug --application "Tutorials-net5-0-DataAccess-RazorPages" --project "ContosoUniversity" --source "github" --strat "database"
# app client --debug --application "Tutorials-net5-0-WebApiApps" --project "TodoApi" --source "github" --strat "api"

# app client --debug --application "Templates-net5-0" --project "Templates-net5-0.WebApp.Base" --source "github"
# app client --debug --application "Templates-net5-0" --project "Templates-net5-0.WebApp.SqlDb" --source "github" --strat "database"
# app client --debug --application "Templates-net5-0" --project "Templates-net5-0.WebApp.Identity" --source "github" --strat "identity"
# app client --debug --application "Templates-net5-0" --project "Templates-net5-0.WebApp.UnitTests" --source "github" --strat "test"
# app client --debug --application "Templates-net5-0" --project "Templates-net5-0.WebApi.Base" --source "github" --strat "api"

# app client --debug --application "DMR" --project "DMR.WebApp" --source "github" --strat "database"
# app client --debug --application "DMR" --project "DMR.WebApp" --source "github" --strat "identity"
# app client --debug --application "SexBound" --project "SexBound.WebApp" --strat "identity" --source=tfsgit
# app client --debug --application "CorruptionOfChampions" --project "CorruptionOfChampions.Conversion" --strat "identity" --source=tfsgit
# app client --debug --application "CorruptionOfChampions" --project "CorruptionOfChampions.WebApp" --strat "identity" --source=tfsgit


# --- Test deploying ARM template to 'Development' environment ---
# app deploy --debug --project "ArmTemplates" --arm "linux/key_vault"
# app deploy --debug --project "ArmTemplates" --arm "linux/key_vault_secret"
# app deploy --debug --project "ArmTemplates" --arm "linux/app_service_plan"
app deploy --debug --project "ArmTemplates" --arm "linux/app_service"
# app deploy --debug --project "ArmTemplates" --arm "linux/sql_server"
app deploy --debug --project "ArmTemplates" --arm "linux/sql_database"
# app deploy --debug --project "ArmTemplates" --arm "linux/storage_account"

# app deploy --debug --project "ArmTemplates" --arm "linked/key_vault_secret"
# app deploy --debug --project "ArmTemplates" --arm "linked/app_service_sql"

# --- Test deploying ARM template to 'Release' environment ---
# app deploy --debug --resource-group="Main" --environment="Prod"
