# Run with PowerShell as Administrator
# https://docs.microsoft.com/en-us/windows/wsl/install-manual

# Download Ubuntu LTS - the preferred, stable release
Invoke-WebRequest -Uri https://aka.ms/wsl-ubuntu-1604 -OutFile $env:temp\Ubuntu.appx -UseBasicParsing
# Install Ubuntu
Add-AppxPackage $env:temp\Ubuntu.appx

# Install RemoteRM (leftover commands in D:\Repos\pc-setup\ansible_playbooks\roles\powershell\files\provision_pc.ps1)

# Launch Ubuntu (uses WSL)
