# PC Setup

## Initialization

1. Run Windows PowerShell (as Administrator) to install Linux on Windows 10

    ``` powershell
    # Change security to TLS 1.2 (required by many sites; more secure than default TLS 1.0)
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    # Install WSL (*nix kernel) - restart system when prompted
    Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux
    # Cache and run the latest script to install Ubuntu + RemoteRM
    $RemoteScript = Invoke-WebRequest https://raw.githubusercontent.com/david-rachwalik/pc-setup/master/win_wsl_install.ps1
    Invoke-Expression $($RemoteScript.Content)
    ```

2. Run Linux Ubuntu (as Administrator) to install Ansible on Linux

    *Linux steps may not work until Windows 10 updates enough*

    ``` bash
    # curl -sL https://raw.githubusercontent.com/david-rachwalik/pc-setup/master/wsl_ansible_install.sh | sudo bash
    sudo git clone https://github.com/david-rachwalik/pc-setup.git ~/pc-setup/
    sudo chmod +x ~/pc-setup/wsl_ansible_install.sh
    sudo chown -R rhodair:rhodair ~/pc-setup/
    sudo -H ~/pc-setup/wsl_ansible_install.sh
    ```

3. Run Ansible on Linux to provision Linux

    ``` bash
    cd ~/pc-setup/ansible_playbooks/
    ansible-playbook wsl_update.yml
    ```

4. Run Ansible on Linux to provision Windows 10

    ``` bash
    cd ~/pc-setup/ansible_playbooks/
    ansible-playbook win_update.yml
    ```

5. Open Visual Studio Code from Linux

    ``` bash
    explorer.exe ~/pc-setup/
    ```

> *Bonus (if not using Ansible)*: Run PowerShell (as Administrator) to [install Chocolatey](https://chocolatey.org/install)

``` powershell
# Run the Chocolatey install script from remote address
Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
# Set Chocolatey to install future packages without confirmation prompts
choco feature enable -n allowGlobalConfirmation
```

## PC Health & Monitoring

### Backup application settings & data

``` bash
ansible home -m include_role -a "name=windows/backup"
```

### Clean and shutdown system

``` bash
ansible home -m include_role -a "name=windows/ccleaner/shutdown"
```

> *For additional examples: view ~/pc-setup/ansible_playbooks/README.md*
