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


# --- Git Steps ---
# https://help.github.com/en/articles/checking-for-existing-ssh-keys
# ls -al ~/.ssh

# https://help.github.com/en/articles/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent
ssh-keygen -f $HOME/.ssh/id_rsa -t rsa -b 4096 -N "" -q
# start the ssh-agent in the background
eval $(ssh-agent -s)
ssh-add ~/.ssh/id_rsa

# https://help.github.com/en/articles/changing-a-remotes-url#switching-remote-urls-from-https-to-ssh
# Update Git remote from HTTPS to SSH
git remote set-url origin git@github.com:david-rachwalik/pc-setup.git
