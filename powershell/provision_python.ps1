# -------- Provision all Python modules & commands --------
# based on E:\Repos\pc-setup\ansible_playbooks\inventories\main\group_vars\windows\python.yml

$pip_packages = @(
    # 'pip'
    'autopep8'
    'pytz'
    'colorlog'
    'yt-dlp'
)

$python_user_modules = @(
    # --- Misc. ---
    'file_backup.py'
    # 'mytest.py'
)

$python_user_boilerplate_modules = @(
    'logging_boilerplate.py'
    'shell_boilerplate.py'
    'azure_boilerplate.py'
    'azure_devops_boilerplate.py'
    'dotnet_boilerplate.py'
    'git_boilerplate.py'
    # 'xml_boilerplate.py'
    # 'multiprocess_boilerplate.py'
    # 'daemon_boilerplate.py'
    # 'socket_boilerplate.py'
)

$python_user_commands = @(
    'app.py'
    'mygit.py'
)


# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------


# -------- Provision PIP (Python package-management system) --------

# --- Upgrade PIP installation ---
Write-Output "Checking for PIP (package manager) upgrades.."
python -m pip install --upgrade pip


# --- Fetch list of installed and out-of-date pip packages ---
# https://stackoverflow.com/questions/62964466/upgrade-outdated-python-packages-by-pip-in-powershell-in-one-line
$pip_packages_installed = (pip list --format=json | ConvertFrom-Json).name
Write-Output "pip_packages_installed: $pip_packages_installed"
$pip_packages_to_install = $pip_packages | Where-Object { $pip_packages_installed -notcontains $_ }
Write-Output "pip_packages_to_install: $pip_packages_to_install"
$pip_packages_outdated = ((pip list --outdated --format=json | ConvertFrom-Json).name | Out-String).replace("`r`n", " ")
Write-Output "pip_packages_outdated: $pip_packages_outdated"


# --- Install missing PIP packages ---

foreach ($package in $pip_packages_to_install)
{
    Write-Output "Attempting to install PIP package '$package'.."
    Write-Output "pip install $package" | Invoke-Expression
}


# --- Upgrade all PIP packages ---
if ($pip_packages_outdated)
{
    Write-Output "Attempting to upgrade PIP package '$package'.."
    Write-Output "pip install --upgrade $pip_packages_outdated" | Invoke-Expression
}

Write-Output "--- Completed provisioning of PIP (package manager) ---"


# -------- Provision Python user modules --------

# Write-Output "python_user_modules:"
# Write-Output ($python_user_modules | Out-String).Trim()
# https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/out-string

# Write-Output "python_user_boilerplate_modules:"
# Write-Output ($python_user_boilerplate_modules | Out-String).Trim()

# Write-Output "python_user_commands:"
# Write-Output ($python_user_commands | Out-String).Trim()


# --- Find Python (source) module locations ---

# $current_dir = Get-Location
# $repo_dir = $PSScriptRoot
# $repo_dir = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$repo_dir = Split-Path $PSScriptRoot -Parent
$repo_py_dir = Join-Path -Path $repo_dir -ChildPath "python"
$repo_py_module_dir = Join-Path -Path $repo_py_dir -ChildPath "modules"
$repo_py_boilerplate_dir = Join-Path -Path $repo_py_module_dir -ChildPath "boilerplates"
$repo_py_command_dir = Join-Path -Path $repo_py_dir -ChildPath "commands"

Write-Output "source directory: $repo_py_dir"


# --- Find Python (destination) site locations ---

$user_py_dir = python -m site --user-base
# Write-Output "user_py_dir: $user_py_dir"

$user_py_module_dir = python -m site --user-site
# Write-Output "user_py_module_dir: $user_py_module_dir"
$user_py_boilerplate_dir = Join-Path -Path $user_py_module_dir -ChildPath "boilerplates"

# https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/join-path
$user_py_command_dir = Join-Path -Path $user_py_dir -ChildPath "bin"
# Write-Output "user_py_command_dir: $user_py_command_dir"

Write-Output "destination directory: $user_py_dir"


# --- Ensure Python (destination) site directories exist ---
# NO LONGER NECESSARY THANKS TO 'ROBOCOPY'
# https://stackoverflow.com/questions/16906170/create-directory-if-it-does-not-exist
# https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.management/test-path
# if (!(Test-Path -PathType Container -Path $user_py_module_dir))
# {
#     Write-Output "Python user-site directory not found, preparing to create.."
#     # https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.management/new-item
#     New-Item -ItemType Directory -Path $user_py_module_dir
#     Write-Output "Python user-site directory was successfully created!"
# }
# # else
# # {
# #     Write-Output "Found the Python user-site directory"
# # }

# if (!(Test-Path -PathType Container -Path $user_py_boilerplate_dir))
# {
#     Write-Output "Python user-site boilerplate directory not found, preparing to create.."
#     # https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.management/new-item
#     New-Item -ItemType Directory -Path $user_py_boilerplate_dir
#     Write-Output "Python user-site boilerplate directory was successfully created!"
# }

# if (!(Test-Path -PathType Container -Path $user_py_command_dir))
# {
#     Write-Output "Python command directory not found, preparing to create.."
#     # https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.management/new-item
#     New-Item -ItemType Directory -Path $user_py_command_dir
#     Write-Output "Python command directory was successfully created!"
# }


# --- Deploy Python user modules ---

[System.Collections.ArrayList]$PythonFilesPassed = @()
[System.Collections.ArrayList]$PythonFilesUpdated = @()

# https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_foreach
foreach ($module in $python_user_modules)
{
    # Get the file hashes
    # https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/join-path
    $src_path = Join-Path -Path $repo_py_module_dir -ChildPath $module
    $dest_path = Join-Path -Path $user_py_module_dir -ChildPath $module
    $src = Get-FileHash $src_path
    $dest = Get-FileHash $dest_path
    # Compare the hashes
    if ($src.Hash -ne $dest.Hash)
    {
        # Write-Output "Hash check failed, preparing to copy '$module'.."
        # https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/robocopy
        # https://adamtheautomator.com/robocopy
        robocopy $repo_py_module_dir $user_py_module_dir $module /mt /z
        # Write-Output "Successfully copied '$module'"
        $PythonFilesUpdated.Add($module) | Out-Null
    }
    else
    {
        # Write-Output "Hash passed: $module"
        $PythonFilesPassed.Add($module) | Out-Null
    }
}
# Write-Output "* Completed provisioning of Python modules"

foreach ($module in $python_user_boilerplate_modules)
{
    # Get the file hashes
    $src_path = Join-Path -Path $repo_py_boilerplate_dir -ChildPath $module
    $dest_path = Join-Path -Path $user_py_boilerplate_dir -ChildPath $module
    $src = Get-FileHash $src_path
    $dest = Get-FileHash $dest_path
    # Compare the hashes
    if ($src.Hash -ne $dest.Hash)
    {
        # Write-Output "Hash check failed, preparing to copy '$module'.."
        robocopy $repo_py_boilerplate_dir $user_py_boilerplate_dir $module /mt /z
        # Write-Output "Successfully copied '$module'"
        $PythonFilesUpdated.Add($module) | Out-Null
    }
    else
    {
        # Write-Output "Hash passed: $module"
        $PythonFilesPassed.Add($module) | Out-Null
    }
}
# Write-Output "* Completed provisioning of Python boilerplate modules"

foreach ($module in $python_user_commands)
{
    # Get the file hashes
    $src_path = Join-Path -Path $repo_py_command_dir -ChildPath $module
    $dest_path = Join-Path -Path $user_py_command_dir -ChildPath $module
    $src = Get-FileHash $src_path
    $dest = Get-FileHash $dest_path
    # Compare the hashes
    if ($src.Hash -ne $dest.Hash)
    {
        # Write-Output "Hash check failed, preparing to copy '$module'.."
        robocopy $repo_py_command_dir $user_py_command_dir $module /mt /z
        # Write-Output "Successfully copied '$module'"
        $PythonFilesUpdated.Add($module) | Out-Null
    }
    else
    {
        # Write-Output "Hash passed: $module"
        $PythonFilesPassed.Add($module) | Out-Null
    }
}
# Write-Output "* Completed provisioning of Python commands"

# Write-Output "Python files that passed the hash check: $PythonFilesPassed"
if ($PythonFilesUpdated)
{
    Write-Output "Python files updated: $PythonFilesUpdated"
}

Write-Output "--- Completed provisioning of Python ---"
