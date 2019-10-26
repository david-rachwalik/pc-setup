# PC Setup

## Initialization

1. Run Windows PowerShell (as Administrator) to install Linux on Windows 10

    ``` powershell
    # Change security to TLS 1.2 (required by many sites; more secure than default TLS 1.0)
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    # Install WSL (*nix kernel) - restart system when prompted
    Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux
    # Cache and run the latest script to install Ubuntu + RemoteRM
    $RemoteScript = Invoke-WebRequest -Uri https://raw.githubusercontent.com/david-rachwalik/pc-setup/master/win_setup.ps1 -UseBasicParsing
    Invoke-Expression $($RemoteScript.Content)
    ```

2. Run Linux Ubuntu to install Ansible on Linux (+step 3)

    ``` bash
    curl -s https://raw.githubusercontent.com/david-rachwalik/pc-setup/master/wsl_setup.sh | sudo -H bash
    ```

3. Run Ansible on Linux to provision Linux

    ``` bash
    cd ~/pc-setup/ansible_playbooks
    ansible-playbook wsl_update.yml
    ```

4. Run Ansible on Linux to provision Windows 10

    ``` bash
    cd ~/pc-setup/ansible_playbooks
    ansible-playbook win_update.yml
    ```

> *Bonus (if not using Ansible)*: Run PowerShell (as Administrator) to [install Chocolatey](https://chocolatey.org/install)

``` powershell
# Run the Chocolatey install script
Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
# Set Chocolatey to skip confirmation prompts
choco feature enable -n allowGlobalConfirmation
```

## PC Health

### Pull latest from GitHub

``` bash
cd ~/pc-setup/ansible_playbooks
git pull
```

### Backup application settings & data

``` bash
ansible home -m include_role -a "name=windows/backup"
```

### Clean and shutdown system

``` bash
ansible home -m include_role -a "name=windows/ccleaner/shutdown"
```

> *[For additional examples](https://github.com/david-rachwalik/pc-setup/tree/master/ansible_playbooks)*

## Development

### Open File Explorer from Linux Ubuntu

``` bash
explorer.exe .
```

### Open VSCode from Linux Ubuntu

``` bash
code ~/pc-setup/
```
