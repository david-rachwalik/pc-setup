#!/bin/bash

# --- Script to quickly iterate upon 'app' command for development ---

cd ~/pc-setup/ansible_playbooks
ansible-playbook system_setup.yml --tags "py" --skip-tags "windows"


# - Test logging into Azure with service principal
# app --debug login

# - Test creating a secret in Azure Key Vault
# app --debug --resource-group="Main" --key-vault="main-keyvault" --secret-key="AutoTestKey" --secret-value="007" secret

# - Test creating a .NET Core webapp
# app --debug --resource-group="Main" app
app client --debug --application "TestApp" --project "TestApp.WebApp" "TestApp.UnitTests"

# - Test deploying an ARM template to development environment
# app --debug --resource-group="Main" deploy

# - Test deploying an ARM template to release environment
# app --debug --resource-group="Main" --environment="Prod" deploy
