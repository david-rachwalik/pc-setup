# Run with PowerShell as Administrator
# https://docs.microsoft.com/en-us/windows/wsl/install-manual

# 1. Install WSL (*nix kernel) and restart system when prompted
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux
# 2. Download Ubuntu LTS - the preferred, stable release
Invoke-WebRequest -Uri https://aka.ms/wsl-ubuntu-1604 -OutFile $env:temp\Ubuntu.appx -UseBasicParsing
# 3. Install Ubuntu
Add-AppxPackage $env:temp\Ubuntu.appx

# 4. Install RemoteRM (leftover commands in D:\Repos\pc-setup\ansible_playbooks\roles\powershell\files\provision_pc.ps1)

# 5. Launch Ubuntu (uses WSL)
