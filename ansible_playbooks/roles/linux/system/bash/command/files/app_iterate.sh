#!/bin/bash

# --- Script to quickly iterate upon 'app' command for development ---

cd ~/pc-setup/ansible_playbooks
ansible-playbook system_setup.yml --tags "py" --skip-tags "windows"


# --- Test Azure login with service principal ---
# app login --debug

# --- Test creating a secret in Azure Key Vault ---
# app secret --debug --resource-group="Main" --key-vault="main-keyvault" --secret-key="AutoTestKey" --secret-value="007"

# --- Test creating an ASP.NET Core WebApp ---
app client --debug --application "Examples" --project "Blank.WebApp" --source "github"
app client --debug --application "Examples" --project "SqlDb.WebApp" --source "github" --strat "database" # template: webapp
# app client --debug --application "Examples" --project "SqlDb.API"
# app client --debug --application "Examples" --project "SqlDb.UnitTests"
# app client --debug --application "Examples" --project "Identity.WebApp" --strat "identity"

# https://docs.microsoft.com/en-us/aspnet/core/tutorials/razor-pages
# app client --debug --application "Tutorials-WebApps-RazorPages" --project "RazorPagesMovie"
# app client --debug --application "Tutorials-DataAccess-RazorPages" --project "ContosoUniversity" --strat "database"
# app client --debug --application "Tutorials-WebApiApps" --project "WebApiApps.API" --strat "api" # authentication: MultiOrg

# app client --debug --application "DMR" --project "DMR.WebApp" --strat "identity"
# app client --debug --application "SexBound" --project "SexBound.WebApp" --strat "identity" --source=tfsgit
# app client --debug --application "CorruptionOfChampions" --project "CorruptionOfChampions.Conversion" --strat "identity" --source=tfsgit
# app client --debug --application "CorruptionOfChampions" --project "CorruptionOfChampions.WebApp" --strat "identity" --source=tfsgit

# --- Test deploying an ARM template to development environment ---
# app deploy --debug --resource-group="Main"

# --- Test deploying an ARM template to release environment ---
# app deploy --debug --resource-group="Main" --environment="Prod"
