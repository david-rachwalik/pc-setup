# https://ohmyposh.dev/docs/themes

# $theme = "default"
$theme = "atomic"
# $theme = "blue-owl"
# $theme = "jandedobbeleer"
$theme = "velvet"

$theme = "unicorn"


# https://ohmyposh.dev/docs/installation/windows (requires system restart before it works in VSCode)
# * prefer the .exe installer to Chocolatey

# [Chocolatey] oh-my-posh has been installed.
# PROFILE: C:\Users\david\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1
# No Powershell profile was found. You may wish to create a profile and append 'Invoke-Expression (oh-my-posh --init --shell pwsh --config " C:\Program Files (x86)/oh-my-posh/themes/themename.omp.json")' to enable oh-my-posh. 'Get-PoshThemes' will list available themes for you

# oh-my-posh --init --shell pwsh --config "$env:USERPROFILE\AppData\Local\Programs\oh-my-posh\themes\$theme.omp.json" | Invoke-Expression

oh-my-posh --init --shell pwsh --config "$Env:LocalAppData\Programs\oh-my-posh\themes\$theme.omp.json" | Invoke-Expression


# https://github.com/devblackops/Terminal-Icons
Import-Module -Name Terminal-Icons