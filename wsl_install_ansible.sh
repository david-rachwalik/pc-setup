#!/bin/bash
export DEBIAN_FRONTEND=noninteractive

# Run command: sudo -H /mnt/d/Repos_Exp/pc-setup/bin/wsl_install_ansible.sh

# Upgrade baseline files of Linux distribution
apt update && apt full-upgrade
# Install Ansible dependencies (Python, Git)
# DEBIAN_FRONTEND=noninteractive apt install -y python-pip git libffi-dev libssl-dev
apt install -y python-pip git libffi-dev libssl-dev
# Install Ansible and WinRM
pip install ansible pywinrm

# Install extra tool to convert Windows files to Linux
# apt install -y dos2unix


# mkdir ~/bin
# Create link in ~/bin to update playbook


# https://azure.microsoft.com/en-us/resources/samples/ansible-playbooks/
# pip install ansible[azure]
# ansible-galaxy install azure.azure_preview_modules
# pip install -r ~/.ansible/roles/azure.azure_preview_modules/files/requirements-azure.txt


# mkdir /etc/ansible/group_vars
# mkdir /etc/ansible/host_vars
# cp /mnt/d/Repos_Exp/pc-setup/etc/ansible/group_vars/windows.yml /etc/ansible/group_vars/windows.yml
# cp /mnt/d/Repos_Exp/pc-setup/etc/ansible/host_vars/localhost.yml /etc/ansible/host_vars/localhost.yml
# cp /mnt/d/Repos_Exp/pc-setup/play_test.yml /etc/ansible/play_test.yml

# https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-apt
# curl -sL https://aka.ms/InstallAzureCLIDeb | bash
