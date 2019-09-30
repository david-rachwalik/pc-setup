# PC Setup

## Initialization

1. Run PowerShell (as Administrator) to install WSL+Ubuntu on Windows 10

    ``` powershell
    # Change security to TLS 1.2 (required by many sites; more secure than default TLS 1.0)
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    # Install WSL (*nix kernel) - restart system when prompted
    Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux
    # Cache the latest script from master branch
    $RemoteScript = Invoke-WebRequest https://raw.githubusercontent.com/david-rachwalik/pc-setup/master/win_wsl_install.ps1
    # Run the script to install Ubuntu and RemoteRM
    Invoke-Expression $($RemoteScript.Content)
    ```

2. Run Ubuntu (as Administrator) to install Ansible on Ubuntu

    ``` bash
    sudo git clone https://github.com/david-rachwalik/pc-setup.git ~/pc-setup/
    sudo -H ~/pc-setup/wsl_ansible_install.sh
    # sudo bash <(curl -sL https://raw.githubusercontent.com/david-rachwalik/pc-setup/master/wsl_ansible_install.sh)
    # curl -sL https://raw.githubusercontent.com/david-rachwalik/pc-setup/master/wsl_ansible_install.sh | sudo bash
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
# Run install script from remote address
Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
# Chocolatey will install packages without confirmation prompts
choco feature enable -n allowGlobalConfirmation
```

## PC Health & Monitoring

### Command to clean and shutdown system

``` bash
ansible home -m include_role -a "name=windows/ccleaner/shutdown"
```

### Backup application settings and update Windows

- backup game saves, screenshots, addons
- backup preferences for productivity programs
- update windows features, install patches, chocolatey upgrade, etc.
- configure security settings

*) For other playbook plans, see TODO.md

Run WSL in Visual Studio Code
<!-- https://stackoverflow.com/questions/11929461/how-can-i-run-dos2unix-on-an-entire-directory -->
find . -type f -print0 | xargs -0 dos2unix
