#!/bin/sh

export DEBIAN_FRONTEND=noninteractive
if test "${SUDO_USER}" != ""; then
    RUN_USER="${SUDO_USER}"
else
    RUN_USER="${USER}"
    echo "This script must be run with 'sudo'"
    exit 1
fi

# Upgrade Linux distribution
apt-get update && apt-get dist-upgrade -y
# Install Ansible dependencies (Python, Git)
apt-get install -y python-pip git libffi-dev libssl-dev
apt-get install -y ansible

if ! test -f /etc/sudoers.d/${RUN_USER}; then
    # Grant user nopasswd sudo access
    # https://gist.github.com/carlessanagustin/922711701b1cfcc5c7a056c7018e8fe2
    touch /etc/sudoers.d/${RUN_USER}
    bash -c "echo '%${RUN_USER} ALL=NOPASSWD:ALL' > /etc/sudoers.d/${RUN_USER}"
    chmod 440 /etc/sudoers.d/${RUN_USER}
    usermod -a -G sudo ${RUN_USER}
fi

# Run remaining commands as user
su -c "curl -s https://raw.githubusercontent.com/david-rachwalik/pc-setup/master/wsl_user_setup.sh | bash" ${RUN_USER}
