#!/bin/sh

# --- This file only to be run as user ---

# Create user bin if it doesn't exist
if ! test -d ~/bin; then
    mkdir ~/bin
    chmod 755 ~/bin
fi

# --- Git Steps ---
# https://help.github.com/en/articles/checking-for-existing-ssh-keys
# Generate SSH keys if they don't exist
if ! test -d ~/.ssh; then
    mkdir ~/.ssh
    chmod 755 ~/.ssh
    # https://help.github.com/en/articles/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent
    ssh-keygen -q -f ${HOME}/.ssh/id_rsa -t rsa -b 4096 -N ""
    # Start the ssh-agent in the background
    eval $(ssh-agent -s)
    ssh-add ~/.ssh/id_rsa
    # Add the contents of your local public key to authorized_keys
    if ! test -f ~/.ssh/authorized_keys; then
        cat ~/.ssh/id_rsa.pub > ~/.ssh/authorized_keys
    fi
    # Add GitHub to known_hosts if it doesn't exist
    if ! test -f ~/.ssh/known_hosts; then
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
# Before using Git in VSCode
git config --global user.name "David Rachwalik"
git config --global user.email "david.rachwalik@outlook.com"
# https://git-scm.com/book/en/v2/Appendix-C%3A-Git-Commands-Setup-and-Config#_core_editor
git config --global core.editor "code --wait"
# View Git settings
# git config --list --show-origin

# Idempotent Git cloning; currently requires manual transfer of SSH to GitHub account before 2nd run
if test -d ~/pc-setup; then
    cd
    rm -rf ~/pc-setup
fi
git clone git@github.com:david-rachwalik/pc-setup.git ~/pc-setup
# https://help.github.com/en/articles/changing-a-remotes-url#switching-remote-urls-from-https-to-ssh
if test -d ~/pc-setup; then
    if test -f /mnt/d/Repos/pc-setup/ansible_playbooks/group_vars/windows/main_vault.yml; then
        cp -f /mnt/d/Repos/pc-setup/ansible_playbooks/group_vars/windows/main_vault.yml ~/pc-setup/ansible_playbooks/group_vars/windows/main_vault.yml
    fi

    # Ansible ignores ansible.cfg in a world-writable directory
    # https://docs.ansible.com/ansible/devel/reference_appendices/config.html#cfg-in-world-writable-dir
    find ~/pc-setup -type d -print0 | xargs -0 chmod 755
    find ~/pc-setup -type f -print0 | xargs -0 chmod 644

    cd ~/pc-setup/ansible_playbooks
    ansible-playbook wsl_update.yml
fi