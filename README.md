            ::: PC Setup :::

1) Install WSL on Windows 10
<!-- - cd /mnt/d/Repos_Exp -->
- git clone https://github.com/david-rachwalik/pc-setup.git
- sudo -H ~/pc-setup/bin/provision_pc.sh
<!-- - sudo -H /mnt/d/Repos_Exp/pc-setup/bin/provision_pc.sh -->

2) Install Ansible on WSL
- git clone https://github.com/david-rachwalik/pc-setup.git
- chmod +x ~/pc-setup/wsl_install_ansible.sh
- sudo -H ~/pc-setup/wsl_install_ansible.sh

3) Use Ansible on WSL to provision WSL
- install software using apt
- configure application settings

4) Use Ansible on WSL to provision Windows 10
- install software using Chocolatey
- configure application settings
- install software not covered by Chocolatey
  - scanner


            ::: PC Health :::

Backup application settings and update Windows:
- backup game saves, screenshots, addons
- backup preferences for productivity programs
- update windows features, install patches, chocolatey upgrade, etc.
- configure security settings

*) For other playbook plans, see TODO.md



Run WSL in Visual Studio Code
<!-- https://stackoverflow.com/questions/11929461/how-can-i-run-dos2unix-on-an-entire-directory -->
find . -type f -print0 | xargs -0 dos2unix

<!-- Commands to initialize new PC:
Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
choco feature enable -n allowGlobalConfirmation -->