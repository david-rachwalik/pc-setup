#!/bin/sh

if test "${SUDO_USER}" != ""; then
    run_user="${SUDO_USER}"
else
    run_user="${USER}"
    echo "This script must be run using 'sudo'"
    exit 1
fi

# Grant user nopasswd sudo access
# https://gist.github.com/carlessanagustin/922711701b1cfcc5c7a056c7018e8fe2
if ! test -f /etc/sudoers.d/${run_user}; then
    touch /etc/sudoers.d/${run_user}
    bash -c "echo '%${run_user} ALL=NOPASSWD:ALL' > /etc/sudoers.d/${run_user}"
    chmod 440 /etc/sudoers.d/${run_user}
    usermod -a -G sudo ${run_user}
fi

# Upgrade Linux distribution
export DEBIAN_FRONTEND=noninteractive
apt-get update && apt-get dist-upgrade -y
# Install Ansible and dependencies
apt-get install -y python3-pip
pip3 install ansible

# Register Microsoft key and feed to prep for .NET SDK
ubuntu_src="https://packages.microsoft.com/config/ubuntu/18.04/packages-microsoft-prod.deb"
ubuntu_tmp="/var/cache/apt/archives/packages-microsoft-prod.deb"
if ! test -f ${ubuntu_tmp}; then
    wget -q ${ubuntu_src} -O ${ubuntu_tmp}
    dpkg -i ${ubuntu_tmp}
fi

# Run remaining commands as user
su -c "curl -s https://raw.githubusercontent.com/david-rachwalik/pc-setup/master/wsl_user_setup.sh | bash" ${run_user}