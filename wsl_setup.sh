#!/bin/bash
export DEBIAN_FRONTEND=noninteractive

echo $USER

# Upgrade baseline files of Linux distribution
# apt update && apt full-upgrade -y
apt-get update && apt-get dist-upgrade -y

# Install Ansible dependencies (Python, Git)
# DEBIAN_FRONTEND=noninteractive apt install -y python-pip git libffi-dev libssl-dev
apt-get install -y python-pip git libffi-dev libssl-dev
# Install Ansible and WinRM
pip install ansible pywinrm


# Create bin directory if it doesn't exist
# if [ ! -d "$HOME/bin" ]; then
#     mkdir $HOME/bin
# fi


# --- Git Steps ---
# https://help.github.com/en/articles/checking-for-existing-ssh-keys
# Generate SSH keys if they don't exist
if [ ! -d ~/.ssh ]; then
    # https://help.github.com/en/articles/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent
    ssh-keygen -f $HOME/.ssh/id_rsa -t rsa -b 4096 -N "" -C "david.rachwalik@outlook.com" -q
    # Start the ssh-agent in the background
    eval $(ssh-agent -s)
    ssh-add ~/.ssh/id_rsa
    # Add the contents of your local public key to authorized_keys
    if [ ! -f ~/.ssh/authorized_keys ]; then
        cat ~/.ssh/id_rsa.pub > ~/.ssh/authorized_keys
    fi
    # Add GitHub to known_hosts if it doesn't exist
    if [ ! -f ~/.ssh/known_hosts ]; then
        touch ~/.ssh/known_hosts
    fi
    ssh-keygen -F github.com || ssh-keyscan -H github.com >> ~/.ssh/known_hosts
    # Copy the public key string to your GitHub Settings
    # sudo view /root/.ssh/id_rsa.pub
    # view ~/.ssh/id_rsa.pub

    # Testing sed command to update SSH config
    # sed 's/^PasswordAuthentication.*/PasswordAuthentication yes/i' /etc/ssh/sshd_config | grep '^PasswordAuthentication.*'
    sed -i 's/^PasswordAuthentication.*/PasswordAuthentication yes/i' /etc/ssh/sshd_config
    sed -i 's/^#PermitRootLogin.*/PermitRootLogin yes/i' /etc/ssh/sshd_config
    # sed 's/.*PubkeyAuthentication.*/PubkeyAuthentication yes/i' /etc/ssh/sshd_config | grep 'PubkeyAuthentication yes'
    sed -i 's/.*PubkeyAuthentication.*/PubkeyAuthentication yes/i' /etc/ssh/sshd_config
    service ssh restart
fi

# https://git-scm.com/book/en/v2/Getting-Started-First-Time-Git-Setup
# View all of your settings
# git config --list --show-origin
# Before using Git in VSCode
git config --global user.name "David Rachwalik"
git config --global user.email "david.rachwalik@outlook.com"
# https://git-scm.com/book/en/v2/Appendix-C%3A-Git-Commands-Setup-and-Config#_core_editor
git config --global core.editor "code --wait"

if [ -d ~/pc-setup ]; then
    rm -rf ~/pc-setup
fi

sudo -u david git clone https://github.com/david-rachwalik/pc-setup.git ~/pc-setup
# git clone git@github.com:david-rachwalik/pc-setup.git ~/pc-setup
# https://help.github.com/en/articles/changing-a-remotes-url#switching-remote-urls-from-https-to-ssh
# Update Git remote from HTTPS to SSH
# git remote set-url origin git@github.com:david-rachwalik/pc-setup.git
echo $USER

# chmod +x ~/pc-setup/wsl_setup.sh
# sudo -H ~/pc-setup/wsl_setup.sh


# https://docs.ansible.com/ansible/devel/reference_appendices/config.html#cfg-in-world-writable-dir
# Ansible will ignore ansible.cfg in a world writable directory (setting directory to user avoids the issue for git clones)
# chown -R david:david ~/pc-setup
# cd ~/pc-setup/ansible_playbooks
ansible-playbook ~/pc-setup/ansible_playbooks/wsl_update.yml
