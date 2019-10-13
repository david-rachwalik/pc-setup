#!/bin/bash

# --- Commands in this file are expected to be done as user ---

# Install Ansible and WinRM (TIP: never sudo pip)
# pip install ansible pywinrm


# Create bin directory if it doesn't exist
# if [ ! -d "$HOME/bin" ]; then
#     mkdir $HOME/bin
# fi


# --- Git Steps ---
# https://help.github.com/en/articles/checking-for-existing-ssh-keys
# Generate SSH keys if they don't exist
if ! test -d ~/.ssh; then
    mkdir ~/.ssh
    chmod 755 ~/.ssh
    # https://help.github.com/en/articles/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent
    ssh-keygen -f $HOME/.ssh/id_rsa -t rsa -b 4096 -N "" -q
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
    # view ~/.ssh/id_rsa.pub

    # Testing sed command to update SSH config
    # sed 's/^PasswordAuthentication.*/PasswordAuthentication yes/i' /etc/ssh/sshd_config | grep '^PasswordAuthentication.*'
    # sudo sed -i 's/^PasswordAuthentication.*/PasswordAuthentication yes/i' /etc/ssh/sshd_config
    # sudo sed -i 's/^#PermitRootLogin.*/PermitRootLogin yes/i' /etc/ssh/sshd_config
    # sudo sed -i 's/.*PubkeyAuthentication.*/PubkeyAuthentication yes/i' /etc/ssh/sshd_config
    # sudo service ssh restart
fi

# https://git-scm.com/book/en/v2/Getting-Started-First-Time-Git-Setup
# View all of your settings
# git config --list --show-origin
# Before using Git in VSCode
git config --global user.name "David Rachwalik"
git config --global user.email "david.rachwalik@outlook.com"
# https://git-scm.com/book/en/v2/Appendix-C%3A-Git-Commands-Setup-and-Config#_core_editor
git config --global core.editor "code --wait"

if test -d ~/pc-setup; then
    cd
    rm -rf ~/pc-setup
    git clone git@github.com:david-rachwalik/pc-setup.git ~/pc-setup
    # https://help.github.com/en/articles/changing-a-remotes-url#switching-remote-urls-from-https-to-ssh

    # Ansible ignores ansible.cfg in a world-writable directory
    # https://docs.ansible.com/ansible/devel/reference_appendices/config.html#cfg-in-world-writable-dir
    find ~/pc-setup -type d -print0 | xargs -0 chmod 755
    find ~/pc-setup -type f -print0 | xargs -0 chmod 644
fi

if test -f /mnt/d/Repos/pc-setup/ansible_playbooks/group_vars/windows/main_vault.yml; then
    cp -f /mnt/d/Repos/pc-setup/ansible_playbooks/group_vars/windows/main_vault.yml ~/pc-setup/ansible_playbooks/group_vars/windows/main_vault.yml
fi

cd ~/pc-setup/ansible_playbooks
ansible-playbook wsl_update.yml