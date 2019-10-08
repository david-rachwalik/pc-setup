# Run with PowerShell as Administrator
# https://docs.microsoft.com/en-us/windows/wsl/install-manual

# Install WSL (*nix kernel) - restart system when prompted
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux
# Download and install Ubuntu LTS - the preferred, stable release
Invoke-WebRequest -Uri https://aka.ms/wsl-ubuntu-1804 -OutFile $env:temp\wsl-ubuntu-1804.appx -UseBasicParsing
Add-AppxPackage $env:temp\wsl-ubuntu-1804.appx
# If you uninstall this package, be sure to fix the registry with CCleaner

# Install RemoteRM (leftover commands in D:\Repos\pc-setup\ansible_playbooks\roles\powershell\files\provision_pc.ps1)

# Launch Ubuntu (uses WSL)
