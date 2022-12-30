# -------- Run with PowerShell (as Administrator) --------

# https://chocolatey.org/packages/*
$choco_packages = @(
    # --- Productivity ---
    'GoogleChrome'
    '7zip'
    'ccleaner'
    'nordvpn'
    'qbittorrent'
    'speccy'

    # --- Development ---
    'powershell-core'
    'python3'
    'oh-my-posh'
    'git'
    'github-desktop'
    # 'docker-desktop'
    'vscode'
    'nodejs-lts'
    # 'dotnetcore-sdk' # 3.1
    'dotnet-6.0-sdk'
    'azure-cli'
    'mongodb'
    'mongodb-compass'
    'mongodb-shell'
    'postman'
    'terraform'

    # --- Media ---
    'geforce-experience'
    'adobereader'
    'AdobeAIR'
    # 'adobeshockwaveplayer'
    'blender'
    'comicrack'
    'spotify'
    # 'unity'
    # 'gimp'

    # --- Video Editing ---
    'k-litecodecpackfull'
    'MakeMKV'
    'handbrake'
    'mkvtoolnix' # https://mkvtoolnix.download/doc/mkvmerge.html
    '4k-video-downloader'
    'obs-studio'
    # 'jubler'
    # 'chatterino'

    # --- Videogames ---
    'directx'
    'steam'
    'discord'
)


# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------


# -------- STAGE 1: Configure PowerShell and OpenSSH --------

# --- Manually ensure PowerShell is updated first (MSI package) ---
# https://learn.microsoft.com/en-us/powershell/scripting/install/installing-powershell-on-windows
# PowerShell 7.2+ has the option to enable Microsoft Update to handle PowerShell updates

# https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_variables
# Variable names in PowerShell are NOT case-sensitive and can include spaces and special characters
# https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_comparison_operators


# --- Allow execution of PowerShell scripts (.ps1) on machine ---
# https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_execution_policies
# - RemoteSigned policy: allows running scripts created locally but downloaded scripts must be digitally signed by a trusted publisher
# - Unrestricted policy: carries no restrictions at all and allows unsigned scripts from any source (default for non-Windows)
$execution_policy = Get-ExecutionPolicy
$expected_policy = "RemoteSigned"
if ($execution_policy -ne $expected_policy)
{
    Write-Output "PowerShell execution policy is '$execution_policy', changing to '$expected_policy'..."
    # https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.security/set-executionpolicy
    Set-ExecutionPolicy -ExecutionPolicy $expected_policy -Force
    Write-Output "PowerShell execution policy successfully changed to '$expected_policy'!"
}


# --- Enable Chocolatey to output as PowerShell objects ---
# TODO: verify whether still necessary
# $powershell_module_chocolatey = Get-InstalledModule -Name chocolatey
# if (-not($powershell_module_chocolatey))
# {
#     Write-Output "PowerShellGet is missing 'chocolatey' Module, preparing to install..."
#     # https://learn.microsoft.com/en-us/powershell/module/powershellget/install-module
#     # https://www.powershellgallery.com/packages/chocolatey/0.0.79
#     Install-Module -Name chocolatey -RequiredVersion 0.0.79 -Force
#     Write-Output "PowerShellGet successfully installed 'chocolatey' Module"
# }


# https://docs.microsoft.com/en-us/windows-server/administration/openssh/openssh_server_configuration
# Set PowerShell as default (instead of Command) for SSH
# New-ItemProperty -Path "HKLM:\SOFTWARE\OpenSSH" -Name DefaultShell -Value "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" -PropertyType String -Force
# Generate public/private keys
# ssh-keygen -q -f %userprofile%/.ssh/id_rsa -t rsa -b 4096 -N ""


# -------- STAGE 2: Install Chocolatey --------

# --- Test Chocolatey baseline installation ---
# $testchoco = Get-Command -Name choco.exe -ErrorAction SilentlyContinue
$choco_version = choco -v
if (-not($choco_version))
{
    Write-Output "Chocolatey is missing, installing..."
    # Set-ExecutionPolicy Bypass -Scope Process -Force; ie ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
    # Set-ExecutionPolicy Bypass -Scope Process -Force; iwr https://chocolatey.org/install.ps1 -UseBasicParsing | iex
    Set-ExecutionPolicy Bypass -Scope Process -Force; Invoke-WebRequest https://chocolatey.org/install.ps1 -UseBasicParsing | Invoke-Expression
    # Allow Chocolatey to skip confirmation prompts
    choco feature enable -n=allowGlobalConfirmation
    # Configure Chocolatey to remember params used for upgrades (to verify: choco feature list)
    # https://docs.chocolatey.org/en-us/guides/create/parse-packageparameters-argument
    choco feature enable -n=useRememberedArgumentsForUpgrades
}
else
{
    Write-Output "Chocolatey install found, version $choco_version"
}


# --- Verify Chocolatey packages as PowerShell object list ---
# https://docs.chocolatey.org/en-us/choco/commands/list
$choco_packages_installed = choco search --local-only --id-only # requires admin
# $choco_packages_type = $choco_packages_installed.GetType()
# $choco_packages_length = $choco_packages_installed.Length
# https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/get-member
# $choco_packages_members = $choco_packages_installed | Get-Member
# $choco_packages_properties = $choco_packages_installed | Get-Member -MemberType Property
# $choco_packages_methods = $choco_packages_installed | Get-Member -MemberType Method

# if ($choco_packages_installed)
# {
#     Write-Output "results of choco search (truthy)"
#     Write-Output "---"
#     Write-Output "choco_packages:"
#     Write-Output ($choco_packages_installed | Out-String).Trim()
#     Write-Output "---"

#     Write-Output "choco_packages_type: $choco_packages_type"
#     Write-Output "choco_packages_length: $choco_packages_length"
#     Write-Output "choco_packages_properties: $choco_packages_properties"

#     $chrome = "GoogleChrome"
#     $chrome_found = $choco_packages_installed -contains $chrome
#     Write-Output "Found $chrome : $chrome_found"
# }
# else
# {
#     Write-Output "results of choco search (falsy)"
# }


# --- Install/Upgrade Chocolatey packages as needed ---
if ($choco_packages_installed)
{
    foreach ($package in $choco_packages | Sort-Object)
    {
        if (-not ($choco_packages_installed -contains $package))
        {
            choco install $package -y
        }
        # else
        # {
        #     choco upgrade $package
        # }
    }
    choco upgrade all
}


# Write-Host "Installing python"
# Start-Process C:\CppBuildTools\Python\python-3.10.7-amd64.exe '/quiet InstallAllUsers=1 PrependPath=1' -wait
# Write-Host "python installation completed successfully"


# --- Run a Python script from PowerShell ---
# Start-Process -FilePath "C:\Program Files\Python\python.exe" -ArgumentList '"c:\scripts\simulate.py" "abcd"';


# -------- STAGE 3: Configure System Platform --------

# --- Set Environmental Variables ---
# https://stackoverflow.com/questions/9546324/adding-a-directory-to-the-path-environment-variable-in-windows
# https://learn.microsoft.com/en-us/powershell/scripting/developer/cmdlet/approved-verbs-for-windows-powershell-commands
function Add-EnvPath
{
    param(
        [Parameter(Mandatory)]
        [string]$Dir
    )
    
    if ( !(Test-Path $Dir) )
    {
        Write-Warning "Supplied directory was not found!"
        return
    }
    $PATH = [Environment]::GetEnvironmentVariable("PATH", "Machine")
    if ( $PATH -notlike "*$($Dir)*" )
    {
        [Environment]::SetEnvironmentVariable("PATH", "$PATH;$Dir", "Machine")
    }
}

$user_py_dir = python -m site --user-base
# https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/join-path
$user_py_command_dir = Join-Path -Path $user_py_dir -ChildPath "bin"
# Write-Output "user_py_command_dir: $user_py_command_dir"
Add-EnvPath $user_py_command_dir

# https://webinstall.dev/pathman
# curl.exe https://webi.ms/pathman | powershell


Write-Output "--- Windows provisioning has completed ---"
Exit


# -------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------


# -------- STAGE 4: Install WSL (Windows Subsystem Linux) --------

# https://docs.microsoft.com/en-us/windows/wsl/install-manual
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux

# --- NOT READY FOR WSL-2 YET... SOON (depends on Ansible) ---
# # Install WSL (*nix kernel) - restart system when prompted - update to WSL 2
# # https://docs.microsoft.com/en-us/windows/wsl/install-manual
# Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux
# Enable-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform
# wsl --set-default-version 2

# Install RemoteRM (leftover commands in D:\Repos\pc-setup\ansible_playbooks\roles\powershell\files\provision_pc.ps1)
$url = "https://raw.githubusercontent.com/ansible/ansible/devel/examples/scripts/ConfigureRemotingForAnsible.ps1"
$file = "${env:temp}\ConfigureRemotingForAnsible.ps1"
(New-Object -TypeName System.Net.WebClient).DownloadFile($url, $file)
powershell.exe -ExecutionPolicy ByPass -File $file
# Verify existing WinRM listeners
# winrm enumerate winrm/config/Listener           # displays IP address and port for HTTP(S)
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

# --- List all installed packages
# Get-AppxPackage -AllUsers
# Get-AppxPackage -Name "CanonicalGroupLimited.UbuntuonWindows" -AllUsers
# Get-AppxPackage -Name "CanonicalGroupLimited.Ubuntu18.04onWindows" -AllUsers
# --- Remove package by name
# Get-AppxPackage *CanonicalGroupLimited.UbuntuonWindows* | Remove-AppxPackage

# Download and install Ubuntu LTS - the preferred, stable release
# $wsl_distro = https://aka.ms/wsl-ubuntu-1804
$wsl_distro = "https://aka.ms/wslubuntu2004"
$wsl_package = "${env:temp}\wsl-ubuntu-2004.appx"
if (-not (Test-Path $wsl_package))
{
    Write-Output "Downloading Ubuntu package (${wsl_package})"
    Invoke-WebRequest -Uri "${wsl_distro}" -OutFile "${wsl_package}" -UseBasicParsing
}
else
{
    Write-Output "Ubuntu package already in temp (${wsl_package})"
}
Add-AppxPackage "${wsl_package}"
# Note: If you reset/uninstall the app, be sure to fix the registry with CCleaner before installing again

# Launch Ubuntu (using WSL)


# -------- STAGE 5: Configure System --------

# --- Provision PowerShell Profile (required for OhMyPosh) ---

$psUserProfile = (Write-Output $PROFILE) # 'echo $PROFILE' command
# https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.management/split-path
$psUserDir = Split-Path -Path $psUserProfile
$psUserProfileFilename = Split-Path -Path $psUserProfile -Leaf # 'Microsoft.PowerShell_profile.ps1'

$repoDir = $PSScriptRoot
# https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/join-path
$repoPsDir = Join-Path -Path $repoDir -ChildPath "powershell"
$repoUserProfile = Join-Path -Path $repoPsDir -ChildPath $psUserProfileFilename

# Verify integrity based on the file hashes
$psProfileSrc = Get-FileHash $repoUserProfile
$psProfileDest = Get-FileHash $psUserProfile
if ($psProfileSrc.Hash -ne $psProfileDest.Hash)
{
    Write-Output "Hash check failed, preparing to update '$psUserProfileFilename'.."
    # https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/robocopy
    # https://adamtheautomator.com/robocopy
    robocopy $repoPsDir $psUserDir $psUserProfileFilename /mt /z
    Write-Output "Successfully updated '$psUserProfileFilename'!"
}
else
{
    Write-Output "Hash passed: $psUserProfileFilename is up-to-date."
}
