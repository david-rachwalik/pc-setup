#!/bin/bash

export DEBIAN_FRONTEND=noninteractive

# Upgrade Linux distribution
apt-get update && apt-get dist-upgrade -y

# Install Ansible dependencies (Python, Git)
apt-get install -y python-pip git libffi-dev libssl-dev

# Run remaining commands as user
# sudo -u david ./wsl_user_setup.sh
sudo -u david curl -s https://raw.githubusercontent.com/david-rachwalik/pc-setup/master/wsl_user_setup.sh | bash
