# -------- Run as Administrator - Provision all Python modules & commands --------
# based on E:\Repos\pc-setup\ansible_playbooks\inventories\main\group_vars\windows\python.yml

$pip_packages = @(
    # 'pip'
    'pytest'
    'autopep8'
    'pytz'
    'colorlog'
    'pylint-quotes'
    'pyinstaller'  # https://pyinstaller.org/en/stable
    'yt-dlp'
    'dirsync'  # https://github.com/tkhyn/dirsync
    # https://learn.microsoft.com/en-us/azure/developer/python/configure-local-development-environment
    # https://learn.microsoft.com/en-us/azure/developer/python/sdk/azure-sdk-overview#connect-to-and-use-azure-resources-with-client-libraries
    'azure-identity'
    'azure-mgmt-resource'
    # https://learn.microsoft.com/en-us/python/api/overview/azure/cosmos-db
    # https://learn.microsoft.com/en-us/azure/developer/python/sdk/examples/azure-sdk-example-database
    'azure-cosmos'
    'azure-mgmt-cosmosdb'
    # https://github.com/Azure-Samples/azure-cosmos-db-mongodb-python-getting-started
    # https://www.mongodb.com/docs/drivers/pymongo
    'pymongo'
    # https://pypi.org/project/python-dotenv
    'python-dotenv'
)
# https://learn.microsoft.com/en-us/azure/cosmos-db/mongodb/quickstart-nodejs

$python_user_modules = @(
    # --- Misc. ---
    'file_backup'
    # 'mytest'
    'app_backup_data'
    'game_backup_data'
)

$python_user_boilerplate_modules = @(
    'logging_boilerplate'
    'shell_boilerplate'
    'azure_boilerplate'
    'azure_devops_boilerplate'
    'dotnet_boilerplate'
    'git_boilerplate'
    # 'xml_boilerplate'
    # 'multiprocess_boilerplate'
    # 'daemon_boilerplate'
    # 'socket_boilerplate'
)

$python_user_commands = @(
    'app'
    'mygit'
    'provision_vscode'
    'pc_clean'
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

# https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_foreach
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


# --- Method to validate files exist and are identical versions ---

# https://learn.microsoft.com/en-us/powershell/scripting/learn/ps101/09-functions
# https://learn.microsoft.com/en-us/powershell/scripting/developer/cmdlet/approved-verbs-for-windows-powershell-commands

# Returns true if both files are found and the hashes match
function Test-FileHashes
{
    param (
        [Parameter(Mandatory)]
        [string]$SourcePath,
        [Parameter(Mandatory)]
        [string]$DestinationPath
    )

    [bool]$result = 0

    # --- Ensure that files exist before attempting to hash ---
    # https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/test-path
    if ((Test-Path -Path $SourcePath -PathType Leaf) -And (Test-Path -Path $DestinationPath -PathType Leaf))
    {
        $src = Get-FileHash $SourcePath
        $dest = Get-FileHash $DestinationPath
        # --- Compare the hashes ---
        if ($src.Hash -eq $dest.Hash)
        {
            $result = 1
        }
    }

    # https://stackoverflow.com/questions/10286164/function-return-value-in-powershell
    return $result
}


# --- Deploy Python user modules & commands ---

[System.Collections.ArrayList]$PythonFilesPassed = @()
[System.Collections.ArrayList]$PythonFilesUpdated = @()

# Provision the latest Python modules
foreach ($module in $python_user_modules)
{
    $filename = "$($module).py"
    $src_path = Join-Path -Path $repo_py_module_dir -ChildPath $filename
    $dest_path = Join-Path -Path $user_py_module_dir -ChildPath $filename
    $match = Test-FileHashes $src_path $dest_path
    if ($match)
    {
        $PythonFilesPassed.Add($filename) | Out-Null
    }
    else
    {
        $PythonFilesUpdated.Add($filename) | Out-Null
        # https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/robocopy
        # https://adamtheautomator.com/robocopy
        robocopy $repo_py_module_dir $user_py_module_dir $filename /mt /z
    }
}

# Provision the latest Python modules (boilerplate)
foreach ($module in $python_user_boilerplate_modules)
{
    $filename = "$($module).py"
    $src_path = Join-Path -Path $repo_py_boilerplate_dir -ChildPath $filename
    $dest_path = Join-Path -Path $user_py_module_dir -ChildPath $filename
    $match = Test-FileHashes $src_path $dest_path
    if ($match)
    {
        $PythonFilesPassed.Add($filename) | Out-Null
    }
    else
    {
        $PythonFilesUpdated.Add($filename) | Out-Null
        robocopy $repo_py_boilerplate_dir $user_py_module_dir $filename /mt /z
    }
}

# Provision the latest Python commands
foreach ($module in $python_user_commands)
{
    $filename = "$($module).py"
    $src_path = Join-Path -Path $repo_py_command_dir -ChildPath $filename
    $dest_path = Join-Path -Path $user_py_command_dir -ChildPath $filename
    $match = Test-FileHashes $src_path $dest_path
    if ($match)
    {
        $PythonFilesPassed.Add($filename) | Out-Null
    }
    else
    {
        $PythonFilesUpdated.Add($filename) | Out-Null
        robocopy $repo_py_command_dir $user_py_command_dir $filename /mt /z
        
        # --- Make the command executable from CLI ---
        $dest_bat_content = "py %AppData%\Python\bin\$($filename) %*"
        $dest_bat = "C:\Python311\Scripts\$($module).bat"
        Set-Content -Path $dest_bat -Value $dest_bat_content -Encoding Ascii

        # --- Make a distributeable application (for external users) ---
        # https://pyinstaller.org/en/stable/usage.html
        # https://realpython.com/pyinstaller-python
        # $dest_build_path = Join-Path -Path $user_py_command_dir -ChildPath 'build'
        # $dest_dist_path = Join-Path -Path $user_py_command_dir -ChildPath 'dist'
        # pyinstaller --onefile --specpath=$dest_build_path --workpath=$dest_build_path --distpath='C:\Python311\Scripts' $dest_path
    }
}

# Write-Output "Python files that passed the hash check: $PythonFilesPassed"
Write-Output "Python files updated: $PythonFilesUpdated"

Write-Output "--- Completed provisioning of Python ---"
