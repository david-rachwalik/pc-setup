# Run with PowerShell as Administrator
# https://docs.microsoft.com/en-us/windows/wsl/install-manual

# Install WSL (*nix kernel) - restart system when prompted
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux

# Install RemoteRM (leftover commands in D:\Repos\pc-setup\ansible_playbooks\roles\powershell\files\provision_pc.ps1)
$url = "https://raw.githubusercontent.com/ansible/ansible/devel/examples/scripts/ConfigureRemotingForAnsible.ps1"
$file = "$env:temp\ConfigureRemotingForAnsible.ps1"
(New-Object -TypeName System.Net.WebClient).DownloadFile($url, $file)
powershell.exe -ExecutionPolicy ByPass -File $file
# Disable WinRM Basic authentication
Set-Item -Path WSMan:\localhost\Service\Auth\Basic -Value false
Set-Item -Path WSMan:\localhost\Service\Auth\Kerberos -Value true
# Verify changes
# winrm get winrm/config/Service
# winrm get winrm/config/Winrs

# Download and install Ubuntu LTS - the preferred, stable release
Invoke-WebRequest -Uri https://aka.ms/wsl-ubuntu-1804 -OutFile $env:temp\wsl-ubuntu-1804.appx -UseBasicParsing
Add-AppxPackage $env:temp\wsl-ubuntu-1804.appx
# Note: If you reset/uninstall the app, be sure to fix the registry with CCleaner before installing again

# Launch Ubuntu (uses WSL)