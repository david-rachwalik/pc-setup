# PC Setup

## Initialization

1. Run Windows PowerShell (as Administrator) to install Linux on Windows

    ``` powershell
    # Change security to TLS 1.2 (required by many sites; more secure than default TLS 1.0)
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    # Install WSL (*nix kernel) - restart system when prompted
    Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux
    # Cache and run the latest script to install Ubuntu + RemoteRM
    $RemoteScript = Invoke-WebRequest -Uri https://raw.githubusercontent.com/david-rachwalik/pc-setup/master/win_setup.ps1 -UseBasicParsing
    Invoke-Expression $($RemoteScript.Content)
    ```

2. Run script to install Ansible on Linux and call provisioning playbooks

    ``` bash
    curl -s https://raw.githubusercontent.com/david-rachwalik/pc-setup/master/wsl_setup.sh | sudo -H bash
    ```

## Development & PC Health

Review aliases to common actions

``` bash
view ~/.bash_aliases
```

Open File Explorer in Linux (only accepts . for path)

``` bash
explorer.exe .
```

Open VSCode in Linux [using CLI](https://code.visualstudio.com/docs/editor/command-line#_core-cli-options)

``` bash
code ~/pc-setup/
```

## Initialization Alternative: Windows Only (No WSL+Ansible)

> *Most actions are only run the first time except `upgrade all`*

1. Run PowerShell (as Administrator) to [install Chocolatey](https://chocolatey.org/install)

    ``` powershell
    # Run the Chocolatey install script
    Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
    # Set Chocolatey to skip confirmation prompts
    choco feature enable -n allowGlobalConfirmation
    ```

2. Search for [Chocolatey packages](https://chocolatey.org/packages) (apps/programs) - *[examples](https://raw.githubusercontent.com/david-rachwalik/pc-setup/master/ansible_playbooks/group_vars/windows/choco.yml)*

3. Install what you like using: `choco install <package>`

4. Upgrade all packages at once using: `choco upgrade all`
