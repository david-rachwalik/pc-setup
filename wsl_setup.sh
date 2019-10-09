#!/bin/bash

export DEBIAN_FRONTEND=noninteractive

# Upgrade Linux distribution
apt-get update && apt-get dist-upgrade -y
# Install Ansible dependencies (Python, Git)
apt-get install -y python-pip git libffi-dev libssl-dev

if [ ! -f /etc/sudoers.d/david ]; then
    # Grant user 'david' nopasswd sudo access
    # https://gist.github.com/carlessanagustin/922711701b1cfcc5c7a056c7018e8fe2
    touch /etc/sudoers.d/david
    bash -c "echo '%david ALL=NOPASSWD:ALL' > /etc/sudoers.d/david"
    chmod 440 /etc/sudoers.d/david
    usermod -a -G sudo david
fi

# Run remaining commands as user
sudo -u david curl -s https://raw.githubusercontent.com/david-rachwalik/pc-setup/master/wsl_user_setup.sh | bash
