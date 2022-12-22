# -------- Provisions all custom Python packages & commands --------
# based on E:\Repos\pc-setup\ansible_playbooks\inventories\main\group_vars\windows\python.yml


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


# Write-Output "python_user_modules:"
# Write-Output ($python_user_modules | Out-String).Trim()
# https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/out-string

# Write-Output "python_user_boilerplate_modules:"
# Write-Output ($python_user_boilerplate_modules | Out-String).Trim()

# Write-Output "python_user_commands:"
# Write-Output ($python_user_commands | Out-String).Trim()


# --- Find Python (source) module locations ---

# $current_dir = Get-Location
$repo_dir = $PSScriptRoot
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
# NOT NECESSARY THANKS TO ROBOCOPY
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

# https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_foreach
foreach ($module in $python_user_modules)
{
    # Get the file hashes
    # https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/join-path
    $src_path = Join-Path -Path $repo_py_module_dir -ChildPath $module
    $src = Get-FileHash $src_path
    $dest_path = Join-Path -Path $user_py_module_dir -ChildPath $module
    $dest = Get-FileHash $dest_path
    # Compare the hashes
    if ($src.Hash -ne $dest.Hash)
    {
        Write-Output "Hash check failed, preparing to copy '$module'.."
        # https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/robocopy
        # https://adamtheautomator.com/robocopy
        robocopy $repo_py_module_dir $user_py_module_dir $module /mt /z
        Write-Output "Successfully copied '$module'"
    }
    else
    {
        Write-Output "Hash passed: $module"
    }
}
Write-Output "* Completed provisioning of Python Modules"

foreach ($module in $python_user_boilerplate_modules)
{
    # Get the file hashes
    $src_path = Join-Path -Path $repo_py_boilerplate_dir -ChildPath $module
    $src = Get-FileHash $src_path
    $dest_path = Join-Path -Path $user_py_boilerplate_dir -ChildPath $module
    $dest = Get-FileHash $dest_path
    # Compare the hashes
    if ($src.Hash -ne $dest.Hash)
    {
        Write-Output "Hash check failed, preparing to copy '$module'.."
        robocopy $repo_py_boilerplate_dir $user_py_boilerplate_dir $module /mt /z
        Write-Output "Successfully copied '$module'"
    }
    else
    {
        Write-Output "Hash passed: $module"
    }
}
Write-Output "* Completed provisioning of Python Boilerplate Modules"

foreach ($module in $python_user_commands)
{
    # Get the file hashes
    $src_path = Join-Path -Path $repo_py_command_dir -ChildPath $module
    $src = Get-FileHash $src_path
    $dest_path = Join-Path -Path $user_py_command_dir -ChildPath $module
    $dest = Get-FileHash $dest_path
    # Compare the hashes
    if ($src.Hash -ne $dest.Hash)
    {
        Write-Output "Hash check failed, preparing to copy '$module'.."
        robocopy $repo_py_command_dir $user_py_command_dir $module /mt /z
        Write-Output "Successfully copied '$module'"
    }
    else
    {
        Write-Output "Hash passed: $module"
    }
}
Write-Output "* Completed provisioning of Python Commands"
