# -------- Run with PowerShell (as Administrator) --------

# can call script with ampersand ("Call operator")
# can run script using the Dot sourcing operator (.) to keep the variables from B in scope of A

# https://stackoverflow.com/questions/4647756/is-there-a-way-to-specify-a-font-color-when-using-write-output
function Write-ColorOutput($ForegroundColor)
{
    # Save the current color
    $fc = [Console]::ForegroundColor
    # Set the new color
    [Console]::ForegroundColor = $ForegroundColor
    # Output
    if ($args)
    {
        Write-Output $args
    }
    else
    {
        $input | Write-Output
    }
    # Restore the original color
    [Console]::ForegroundColor = $fc
}


# -------- Provision the system platform --------

# --- PowerShell Scripts ---

# Determine PowerShell script directory
$script_root = $PSScriptRoot
$repo_dir = Split-Path $script_root -Parent
$repo_powershell_dir = Join-Path -Path $repo_dir -ChildPath "powershell"
Write-Output "PowerShell source directory: $repo_powershell_dir"

# Provision Chocolatey
$prov_choco_script = Join-Path -Path $repo_powershell_dir -ChildPath "provision_chocolatey.ps1"
& $prov_choco_script

# TODO: Update system registry
$prov_registry_script = Join-Path -Path $repo_powershell_dir -ChildPath "registry.ps1"
& $prov_registry_script

# Provision Python
$prov_python_script = Join-Path -Path $repo_powershell_dir -ChildPath "provision_python.ps1"
& $prov_python_script

# --- Python Scripts ---

# Provision Visual Studio Code
& "provision_vscode"

# Provision Azure CLI
& "provision_azure"

# Provision Angular
# & "provision_angular"

# Provision .NET Framework
# based on /ansible_playbooks/roles/windows/apps/dotnet/setup/tasks/main.yml
# & "provision_dotnet"


Write-ColorOutput Green "--- Completed PC Setup ---"
