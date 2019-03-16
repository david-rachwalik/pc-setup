# https://chocolatey.org/docs/ChocolateyFAQs#what-is-the-difference-between-packages-no-suffix-as-compared-to-install-portable

# -------- Only Need To Run Once --------

Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

# https://stackoverflow.com/questions/29873439/how-do-i-update-all-chocolatey-applications-without-confirmation
choco feature enable -n allowGlobalConfirmation
choco feature disable -n=allowGlobalConfirmation

choco feature enable -n=autoUninstaller


# -------- Common Commands --------

# List all locally installed packages
choco list --localonly

# List all outdated packages
choco outdated

# https://superuser.com/questions/890251/how-to-list-chocolatey-packages-already-installed-and-newer-version-available-fr
# Full breakdown summary of outdated packages and upgrade version available
choco upgrade all --noop
