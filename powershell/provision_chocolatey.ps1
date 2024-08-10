# -------- Run with PowerShell (as Administrator) --------

# https://chocolatey.org/packages/*
$choco_packages = @(
    # --- Productivity ---
    'GoogleChrome'
    'speccy'
    'procexp'
    'tcpview'
    '7zip'
    'ccleaner'
    'nordvpn'
    '4k-video-downloader'
    'qbittorrent'
    'chatgpt'

    # --- Development ---
    'powershell-core'
    'python3'
    'oh-my-posh'
    'git'
    'github-desktop'
    'vscode'
    'docker-desktop'
    'docker-compose'
    # (apps that could be limited to containers)
    'nodejs-lts'
    # 'dotnetcore-sdk' # 3.1
    'dotnet-6.0-sdk'
    'azure-cli'
    'mongodb'
    'mongodb-compass'
    'mongodb-shell'
    'postman'
    'terraform'
    'upx' # Ultimate Packer for eXecutables (for PyInstaller)
    'ruby' # mainly for Jekyll (gem install jekyll bundler)

    # --- Media ---
    'geforce-experience'
    'adobereader'
    'AdobeAIR'
    # 'adobeshockwaveplayer'
    'comicrack'
    'spotify'
    # 'gimp'
    'blender'
    # 'unity'

    # --- Video Editing ---
    'k-litecodecpackfull'
    'handbrake'
    'lossless-cut'
    'MakeMKV'
    'mkvtoolnix' # https://mkvtoolnix.download/doc/mkvmerge.html
    # 'jubler'
    
    # --- Streaming ---
    'obs-studio'
    # 'chatterino'
    'chatterino7'

    # --- Videogames ---
    'directx'
    'steam'
    'discord'
    'reshade'
    # Example of using params
    # 'reshade --params "/Desktop /NoStartMenu"'
    # 'winpinator' # for Steam Deck file transfer
)

# Additional packages only for desktop systems
$choco_packages_extra = @(
    # --- Productivity ---
    'vmware-player' # free version of VMWare virtualization software
    'vmware-tools' # utilities to enhance virtual machine performance
    # 'vmware-workstation-player' # paid version of VMWare Player with additional features
)


# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------


# --- Verify Chocolatey installation ---
# $testchoco = Get-Command -Name choco.exe -ErrorAction SilentlyContinue
$choco_version = choco -v
if (-not($choco_version))
{
    Write-Host "Chocolatey is missing, installing..." -ForegroundColor Yellow
    # Set-ExecutionPolicy Bypass -Scope Process -Force; ie ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
    # Set-ExecutionPolicy Bypass -Scope Process -Force; iwr https://chocolatey.org/install.ps1 -UseBasicParsing | iex
    Set-ExecutionPolicy Bypass -Scope Process -Force; Invoke-WebRequest https://chocolatey.org/install.ps1 -UseBasicParsing | Invoke-Expression
    # choco feature list (https://docs.chocolatey.org/en-us/choco/commands/feature)
    # Allow Chocolatey to skip confirmation prompts
    choco feature enable -n=allowGlobalConfirmation
    # Configure Chocolatey to remember params used for upgrades
    # https://docs.chocolatey.org/en-us/guides/create/parse-packageparameters-argument
    choco feature enable -n=useRememberedArgumentsForUpgrades
}
else
{
    Write-Host "Chocolatey install found, version $choco_version"
}


# --- Enable Chocolatey to output as PowerShell objects ---
# TODO: verify whether still necessary
# $powershell_module_chocolatey = Get-InstalledModule -Name chocolatey
# if (-not($powershell_module_chocolatey))
# {
#     Write-Host "PowerShellGet is missing 'chocolatey' Module, preparing to install..." -ForegroundColor Yellow
#     # https://learn.microsoft.com/en-us/powershell/module/powershellget/install-module
#     # https://www.powershellgallery.com/packages/chocolatey/0.0.79
#     Install-Module -Name chocolatey -RequiredVersion 0.0.79 -Force
#     Write-Host "PowerShellGet successfully installed 'chocolatey' Module"
# }


# --- Verify Chocolatey packages ---
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
#     Write-Host "results of choco search (truthy)" -ForegroundColor Green
#     Write-Host "---"
#     Write-Host "choco_packages:"
#     Write-Host ($choco_packages_installed | Out-String).Trim()
#     Write-Host "---"

#     Write-Host "choco_packages_type: $choco_packages_type"
#     Write-Host "choco_packages_length: $choco_packages_length"
#     Write-Host "choco_packages_properties: $choco_packages_properties"

#     $chrome = "GoogleChrome"
#     $chrome_found = $choco_packages_installed -contains $chrome
#     Write-Host "Found $chrome : $chrome_found"
# }
# else
# {
#     Write-Host "results of choco search (falsy)" -ForegroundColor Red
# }


# --- Install/Upgrade Chocolatey packages as needed ---
if ($choco_packages_installed)
{
    foreach ($package in $choco_packages | Sort-Object)
    {
        if (-not ($choco_packages_installed -contains $package))
        {
            # Install missing Chocolatey package
            choco install $package -y
        }
        # else
        # {
        #     choco upgrade $package
        # }
    }
    # Update all Chocolatey packages
    choco upgrade all
}


# Remove shortcuts from desktop
Remove-Item "$Env:HomeDrive\Users\*\Desktop\*.lnk" -Force  # C drive
$DesktopPath = [Environment]::GetFolderPath("Desktop")
Remove-Item "$DesktopPath\*.lnk" -Force  # OneDrive


Write-Host "--- Completed provisioning of Chocolatey ---" -ForegroundColor Green
