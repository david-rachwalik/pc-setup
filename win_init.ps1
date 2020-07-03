# Run with PowerShell as Administrator

# https://docs.microsoft.com/en-us/windows-server/administration/openssh/openssh_server_configuration
# Set PowerShell as default (instead of Command) for SSH
# New-ItemProperty -Path "HKLM:\SOFTWARE\OpenSSH" -Name DefaultShell -Value "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" -PropertyType String -Force
# Generate public/private keys
# ssh-keygen -q -f %userprofile%/.ssh/id_rsa -t rsa -b 4096 -N ""

# Install Chocolatey
Set-ExecutionPolicy Bypass -Scope Process -Force; iwr https://chocolatey.org/install.ps1 -UseBasicParsing | iex

# Install WSL (*nix kernel) - restart system when prompted - update to WSL 2
# https://docs.microsoft.com/en-us/windows/wsl/install-manual
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux
Enable-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform
wsl --set-default-version 2

# Install RemoteRM (leftover commands in D:\Repos\pc-setup\ansible_playbooks\roles\powershell\files\provision_pc.ps1)
$url = "https://raw.githubusercontent.com/ansible/ansible/devel/examples/scripts/ConfigureRemotingForAnsible.ps1"
$file = "$env:temp\ConfigureRemotingForAnsible.ps1"
(New-Object -TypeName System.Net.WebClient).DownloadFile($url, $file)
powershell.exe -ExecutionPolicy ByPass -File $file
# Verify existing WinRM listeners
winrm enumerate winrm/config/Listener
# Toggle WinRM authentications
# Set-Item -Path WSMan:\localhost\Service\Auth\Basic -Value true
# Set-Item -Path WSMan:\localhost\Service\Auth\Kerberos -Value false
# Verify changes
# winrm get winrm/config/Service
# winrm get winrm/config/Winrs

# To permanently allow .ps1 scripts on machine
# https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_execution_policies
# https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.security/set-executionpolicy
Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Force

# Ensure correct network connection type for remoting (possibly not needed for Auth\Basic)
# Set-NetConnectionProfile -NetworkCategory Private
# winrm quickconfig -quiet
# Verify Windows IP Configuration
# winrs -r:DESKTOP-U8ATCTC ipconfig /all

# --- List all installed packages
# Get-AppxPackage -AllUsers
# Get-AppxPackage -Name "CanonicalGroupLimited.UbuntuonWindows" -AllUsers
# Get-AppxPackage -Name "CanonicalGroupLimited.Ubuntu18.04onWindows" -AllUsers
# --- Remove package by name
# Get-AppxPackage *CanonicalGroupLimited.UbuntuonWindows* | Remove-AppxPackage

# Download and install Ubuntu LTS - the preferred, stable release
Invoke-WebRequest -Uri https://aka.ms/wsl-ubuntu-2004 -OutFile $env:temp\wsl-ubuntu-2004.appx -UseBasicParsing
Add-AppxPackage $env:temp\wsl-ubuntu-2004.appx
# Note: If you reset/uninstall the app, be sure to fix the registry with CCleaner before installing again

# Launch Ubuntu (uses WSL)