#!/bin/bash
export DEBIAN_FRONTEND=noninteractive

# Upgrade baseline files of Linux distribution
# apt update && apt full-upgrade -y
apt-get update && apt-get dist-upgrade -y

# Install Ansible dependencies (Python, Git)
# DEBIAN_FRONTEND=noninteractive apt install -y python-pip git libffi-dev libssl-dev
apt-get install -y python-pip git libffi-dev libssl-dev
# Install Ansible and WinRM
pip install ansible pywinrm