#!/bin/bash

export DEBIAN_FRONTEND=noninteractive

# Upgrade Linux distribution
apt-get update && apt-get dist-upgrade -y
# Install Ansible dependencies (Python, Git)
apt-get install -y python-pip git libffi-dev libssl-dev

if [ ! -f /etc/sudoers.d/$SUDO_USER ]; then
    # Grant user nopasswd sudo access
    # https://gist.github.com/carlessanagustin/922711701b1cfcc5c7a056c7018e8fe2
    touch /etc/sudoers.d/$SUDO_USER
    userGroupCommand = "echo '%" + $SUDO_USER + " ALL=NOPASSWD:ALL' > /etc/sudoers.d/" + $SUDO_USER
    bash -c $userGroupCommand
    chmod 440 /etc/sudoers.d/$SUDO_USER
    usermod -a -G sudo $SUDO_USER
fi

# Run remaining commands as user
su -c "curl -s https://raw.githubusercontent.com/david-rachwalik/pc-setup/master/wsl_user_setup.sh | bash" $SUDO_USER
