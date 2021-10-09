#!/bin/bash

# --- Example Commands ---
# setup --tags sh
# app_iterate


# --- Script to quickly iterate upon 'app' command for development ---

cd ~/pc-setup/ansible_playbooks
ansible-playbook system_setup.yml --tags "py" --skip-tags "windows"


# -------- (old, transfer to templates) Test creating an ASP.NET Core WebApp --------
# app client --debug --application "Examples" --project "Blank.WebApp" --source "github"
# app client --debug --application "Examples" --project "SqlDb.WebApp" --source "github" --strat "database" # template: webapp
# https://docs.microsoft.com/en-us/azure/active-directory/develop/tutorial-v2-asp-webapp
# https://docs.microsoft.com/en-us/aspnet/core/security/authentication/scaffold-identity
# https://docs.microsoft.com/en-us/aspnet/core/fundamentals/tools/dotnet-aspnet-codegenerator (Scaffold CLI options)
# app client --debug --application "Examples" --project "Identity.WebApp" --strat "identity"
# https://docs.microsoft.com/en-us/aspnet/core/tutorials/first-web-api
# https://github.com/azuread/microsoft-identity-web/wiki/web-apis
# app client --debug --application "Examples" --project "Identity.API"
# app client --debug --application "Examples" --project "Identity.UnitTests"

# -------- (old, remove) Test deploying an ARM template to development environment --------
# app deploy --debug --application "ArmMock" --arm "all/blank"
# app deploy --debug --application "ArmMock" --arm "linux/webapp_blank"


# --- Test Azure login with service principal ---
# app login --debug

# --- Test creating a secret in Azure Key Vault ---
# app secret --debug --resource-group="Main" --key-vault="main-keyvault" --secret-key="AutoTestKey" --secret-value="007"

# --- Test creating an ASP.NET Core WebApp ---
# app client --debug --application "Tutorials-net3-1-WebApps-RazorPages" --project "RazorPagesMovie" --source "github" --framework "netcoreapp3.1"
# app client --debug --application "Tutorials-net3-1-DataAccess-RazorPages" --project "ContosoUniversity" --source "github" --framework "netcoreapp3.1" --strat "database"
# app client --debug --application "Tutorials-net5-0-WebApps-RazorPages" --project "RazorPagesMovie" --source "github"
# app client --debug --application "Tutorials-net5-0-DataAccess-RazorPages" --project "ContosoUniversity" --source "github" --strat "database"
# app client --debug --application "Tutorials-net5-0-WebApiApps" --project "TodoApi" --source "github" --strat "api"

# app client --debug --application "Templates-net5-0" --project "Templates-net5-0.Base.WebApp" --source "github"
# app client --debug --application "Templates-net5-0" --project "Templates-net5-0.SqlDb.WebApp" --source "github" --strat "database"
# app client --debug --application "Templates-net5-0" --project "Templates-net5-0.Identity.WebApp" --source "github" --strat "identity"
# app client --debug --application "Templates-net5-0" --project "Templates-net5-0.Base.WebApi" --source "github" --strat "api"

# app client --debug --application "DMR" --project "DMR.WebApp" --source "github" --strat "database"
# app client --debug --application "DMR" --project "DMR.WebApp" --source "github" --strat "identity"
# app client --debug --application "SexBound" --project "SexBound.WebApp" --strat "identity" --source=tfsgit
# app client --debug --application "CorruptionOfChampions" --project "CorruptionOfChampions.Conversion" --strat "identity" --source=tfsgit
# app client --debug --application "CorruptionOfChampions" --project "CorruptionOfChampions.WebApp" --strat "identity" --source=tfsgit


# --- Test deploying ARM template to 'Development' environment ---
# app deploy --debug --application "ArmTemplates" --arm "linux/key_vault"
# app deploy --debug --application "ArmTemplates" --arm "linux/key_vault_secret"
# app deploy --debug --application "ArmTemplates" --arm "linked/key_vault_secret"

# app deploy --debug --application "ArmTemplates" --arm "linux/sql_server"
app deploy --debug --application "ArmTemplates" --arm "linux/sql_database"

# app deploy --debug --application "ArmTemplates" --arm "linux/app_service_plan"
# app deploy --debug --application "ArmTemplates" --arm "linux/webapp_sql"
# app deploy --debug --application "ArmTemplates" --arm "linux/webapi_sql"

# --- Test deploying ARM template to 'Release' environment ---
# app deploy --debug --resource-group="Main" --environment="Prod"
