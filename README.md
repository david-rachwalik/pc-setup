# PC Setup

## Initialization

1. Run Windows PowerShell (as Administrator) to install Linux on Windows 10

    ``` powershell
    # Change security to TLS 1.2 (required by many sites; more secure than default TLS 1.0)
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    # Install WSL (*nix kernel) - restart system when prompted
    Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux
    # Cache and run the latest script to install Ubuntu + RemoteRM
    $RemoteScript = Invoke-WebRequest https://raw.githubusercontent.com/david-rachwalik/pc-setup/master/win_setup.ps1
    Invoke-Expression $($RemoteScript.Content)
    ```

2. Run Linux Ubuntu (as Administrator) to install Ansible on Linux

    [[REF](https://docs.ansible.com/ansible/devel/reference_appendices/config.html#cfg-in-world-writable-dir)] *Ansible will ignore ansible.cfg in a world writable directory*

    ``` bash
    # curl -sL https://raw.githubusercontent.com/david-rachwalik/pc-setup/master/wsl_setup.sh | sudo bash
    sudo git clone https://github.com/david-rachwalik/pc-setup.git ~/pc-setup/
    sudo chmod +x ~/pc-setup/wsl_setup.sh
    sudo chown -R david:david ~/pc-setup/
    sudo -H ~/pc-setup/wsl_setup.sh
    # Copy the public key string to your GitHub Settings
    view ~/.ssh/id_rsa.pub
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

## Development

### Open File Explorer from Linux

``` bash
explorer.exe ~/pc-setup/
```

### Open VSCode from Linux

``` bash
code ~/pc-setup/
```

### Before using Git in VSCode

``` bash
git config --global user.email "you@example.com"
git config --global user.name "Your Name"
```
