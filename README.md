# PC Setup

## Initialization

1. Use PowerShell (Admin mode) to install WSL+Ubuntu on Windows 10

    ``` powershell
    Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://github.com/david-rachwalik/pc-setup/win_wsl_install.ps1'))
    ```

2. Use Ubuntu (Admin mode) to install Ansible on Ubuntu

    ``` bash
    git clone https://github.com/david-rachwalik/pc-setup.git
    chmod -R +x ~/pc-setup/
    sudo -H ~/pc-setup/wsl_ansible_install.sh
    ```

3. Use Ansible on Ubuntu to provision Ubuntu
    - install software using apt
    - configure application settings

4. Use Ansible on Ubuntu to provision Windows 10
    - install software using Chocolatey
    - configure application settings
    - install software not covered by Chocolatey
      - scanner

> *Bonus (if not using Ansible)*:  Use PowerShell (Admin mode) to [install Chocolatey](https://chocolatey.org/install)

``` powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('[https://chocolatey.org/install.ps1](https://chocolatey.org/install.ps1)'))
choco feature enable -n allowGlobalConfirmation
```

## PC Health & Monitoring

### Backup application settings and update Windows

- backup game saves, screenshots, addons
- backup preferences for productivity programs
- update windows features, install patches, chocolatey upgrade, etc.
- configure security settings

*) For other playbook plans, see TODO.md

Run WSL in Visual Studio Code
<!-- https://stackoverflow.com/questions/11929461/how-can-i-run-dos2unix-on-an-entire-directory -->
find . -type f -print0 | xargs -0 dos2unix
