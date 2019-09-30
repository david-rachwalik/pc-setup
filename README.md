# PC Setup

## Initialization

1. Run PowerShell (as Administrator) to install WSL+Ubuntu on Windows 10

    ``` powershell
    # Change security to TLS 1.2 (required by many sites; more secure than default TLS 1.0)
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    # Run install script from remote address
    # Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://github.com/david-rachwalik/pc-setup/blob/master/win_wsl_install.ps1'))

    # Get the latest raw script from master branch
    $RemoteScript = Invoke-WebRequest https://raw.githubusercontent.com/david-rachwalik/pc-setup/master/win_wsl_install.ps1
    # Run the script
    Invoke-Expression $($RemoteScript.Content)
    ```

2. Run Ubuntu (as Administrator) to install Ansible on Ubuntu

    ``` bash
    git clone https://github.com/david-rachwalik/pc-setup.git
    chmod -R +x ~/pc-setup/
    sudo -H ~/pc-setup/wsl_ansible_install.sh
    ```

3. Run Ansible on Ubuntu to provision Ubuntu
    - install software using apt
    - configure application settings

4. Run Ansible on Ubuntu to provision Windows 10
    - install software using Chocolatey
    - configure application settings
    - install software not covered by Chocolatey
      - scanner

> *Bonus (if not using Ansible)*: Run PowerShell (as Administrator) to [install Chocolatey](https://chocolatey.org/install)

``` powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
# Chocolatey will install packages without confirmation prompts
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
