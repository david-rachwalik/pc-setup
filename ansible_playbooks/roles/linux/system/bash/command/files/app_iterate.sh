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
# https://docs.microsoft.com/en-us/azure/active-directory/develop/tutorial-v2-asp-webapp
# https://docs.microsoft.com/en-us/aspnet/core/security/authentication/scaffold-identity
# https://docs.microsoft.com/en-us/aspnet/core/fundamentals/tools/dotnet-aspnet-codegenerator (Scaffold CLI options)
# app client --debug --application "Examples" --project "Identity.WebApp" --strat "identity"
# https://docs.microsoft.com/en-us/aspnet/core/tutorials/first-web-api
# https://github.com/azuread/microsoft-identity-web/wiki/web-apis
# app client --debug --application "Examples" --project "Identity.API"
# app client --debug --application "Examples" --project "Identity.UnitTests"

# https://docs.microsoft.com/en-us/aspnet/core/tutorials/razor-pages
# app client --debug --application "Tutorials-net3-1-WebApps-RazorPages" --project "RazorPagesMovie" --source "github" --framework "netcoreapp3.1"
# app client --debug --application "Tutorials-net3-1-DataAccess-RazorPages" --project "ContosoUniversity" --source "github" --framework "netcoreapp3.1" --strat "database"
app client --debug --application "Tutorials-net5-0-WebApps-RazorPages" --project "RazorPagesMovie" --source "github"
app client --debug --application "Tutorials-net5-0-DataAccess-RazorPages" --project "ContosoUniversity" --source "github" --strat "database"
# app client --debug --application "Tutorials-WebApiApps" --project "WebApiApps.API" --source "github" --strat "api" # authentication: MultiOrg

# app client --debug --application "DMR" --project "DMR.WebApp" --strat "identity"
# app client --debug --application "SexBound" --project "SexBound.WebApp" --strat "identity" --source=tfsgit
# app client --debug --application "CorruptionOfChampions" --project "CorruptionOfChampions.Conversion" --strat "identity" --source=tfsgit
# app client --debug --application "CorruptionOfChampions" --project "CorruptionOfChampions.WebApp" --strat "identity" --source=tfsgit

# --- Test deploying an ARM template to development environment ---
# app deploy --debug --resource-group="Main"

# --- Test deploying an ARM template to release environment ---
# app deploy --debug --resource-group="Main" --environment="Prod"
