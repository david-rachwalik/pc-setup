# Run with PowerShell (as Administrator)

# https://chocolatey.org/packages/*
$choco_packages_to_install = @(
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


# --- Verify Chocolatey installation ---
# $testchoco = Get-Command -Name choco.exe -ErrorAction SilentlyContinue
$choco_version = choco -v
if (-not($choco_version))
{
    Write-Output "Chocolatey is missing, installing..."
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
    Write-Output "Chocolatey install found, version $choco_version"
}


# --- Verify Chocolatey packages ---
# https://docs.chocolatey.org/en-us/choco/commands/list
$choco_packages = choco search --local-only --id-only # requires admin
# $choco_packages_type = $choco_packages.GetType()
# $choco_packages_length = $choco_packages.Length
# https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/get-member
# $choco_packages_members = $choco_packages | Get-Member
# $choco_packages_properties = $choco_packages | Get-Member -MemberType Property
# $choco_packages_methods = $choco_packages | Get-Member -MemberType Method

# if ($choco_packages)
# {
#     Write-Output "results of choco search (truthy)"
#     Write-Output "---"
#     Write-Output "choco_packages:"
#     Write-Output ($choco_packages | Out-String).Trim()
#     Write-Output "---"

#     Write-Output "choco_packages_type: $choco_packages_type"
#     Write-Output "choco_packages_length: $choco_packages_length"
#     Write-Output "choco_packages_properties: $choco_packages_properties"

#     $chrome = "GoogleChrome"
#     $chrome_found = $choco_packages -contains $chrome
#     Write-Output "Found $chrome : $chrome_found"
# }
# else
# {
#     Write-Output "results of choco search (falsy)"
# }


if ($choco_packages)
{
    foreach ($package in $choco_packages_to_install | Sort-Object)
    {
        if (-not ($choco_packages -contains $package))
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


Write-Output "--- Successfully completed Chocolatey provisioning! ---"
