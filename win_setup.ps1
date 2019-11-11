# Run with PowerShell as Administrator

# Install Chocolatey
Set-ExecutionPolicy Bypass -Scope Process -Force; iwr https://chocolatey.org/install.ps1 -UseBasicParsing | iex

# Install WSL (*nix kernel) - restart system when prompted
# https://docs.microsoft.com/en-us/windows/wsl/install-manual
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux

# Install RemoteRM (leftover commands in D:\Repos\pc-setup\ansible_playbooks\roles\powershell\files\provision_pc.ps1)
$url = "https://raw.githubusercontent.com/ansible/ansible/devel/examples/scripts/ConfigureRemotingForAnsible.ps1"
$file = "$env:temp\ConfigureRemotingForAnsible.ps1"
(New-Object -TypeName System.Net.WebClient).DownloadFile($url, $file)
powershell.exe -ExecutionPolicy ByPass -File $file
# Toggle WinRM authentications
# Set-Item -Path WSMan:\localhost\Service\Auth\Basic -Value true
# Set-Item -Path WSMan:\localhost\Service\Auth\Kerberos -Value false
# Verify changes
# winrm get winrm/config/Service
# winrm get winrm/config/Winrs

# Ensure correct network connection type for remoting (possibly not needed for Auth\Basic)
# Set-NetConnectionProfile -NetworkCategory Private
# winrm quickconfig -quiet
# Verify Windows IP Configuration
# winrs -r:DESKTOP-U8ATCTC ipconfig /all
# Verify existing WinRM listeners
# winrm enumerate winrm/config/Listener

# Download and install Ubuntu LTS - the preferred, stable release
Invoke-WebRequest -Uri https://aka.ms/wsl-ubuntu-1804 -OutFile $env:temp\wsl-ubuntu-1804.appx -UseBasicParsing
Add-AppxPackage $env:temp\wsl-ubuntu-1804.appx
# Note: If you reset/uninstall the app, be sure to fix the registry with CCleaner before installing again

# Launch Ubuntu (uses WSL)