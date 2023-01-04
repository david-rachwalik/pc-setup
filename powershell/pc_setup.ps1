# -------- Run with PowerShell (as Administrator) --------

# can call script with ampersand ("Call operator")
# can run script using the Dot sourcing operator (.) to keep the variables from B in scope of A


# -------- Provision the system platform --------

# --- Determine PowerShell script directory ---
$script_root = $PSScriptRoot
$repo_dir = Split-Path $script_root -Parent
$repo_powershell_dir = Join-Path -Path $repo_dir -ChildPath "powershell"
Write-Host "PowerShell source directory: $repo_powershell_dir"

# --- Provision Chocolatey ---
$prov_choco_script = Join-Path -Path $repo_powershell_dir -ChildPath "provision_chocolatey.ps1"
& $prov_choco_script

# --- Provision Python ---
$prov_python_script = Join-Path -Path $repo_powershell_dir -ChildPath "provision_python.ps1"
& $prov_python_script



Write-Host "--- Completed PC Setup ---" -ForegroundColor Green
