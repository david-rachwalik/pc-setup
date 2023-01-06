# -------- Run with PowerShell (as Administrator) --------

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


# -------- Scheduled Tasks (Daily) --------

# --- PC Setup ---
$taskName = "CRON PC Clean"
# $taskExists = Get-ScheduledTask | Where-Object { $_.TaskName -like $taskName }
$taskExists = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if (!$taskExists)
{
    Write-Output "Scheduled task '$taskName' does not exist."
    # $action = New-ScheduledTaskAction -Execute "pwsh" -Argument "E:\Repos\pc-setup\powershell\pc_setup.ps1"
    $py_exe = "C:\Python311\python.exe"
    $py_script = "$Env:AppData\Python\bin\pc_clean.py"
    $action = New-ScheduledTaskAction -Execute $py_exe -Argument $py_script
    $trigger = New-ScheduledTaskTrigger -Daily -At "3am"
    Register-ScheduledTask -TaskName $taskName -RunLevel "Highest" -Action $action -Trigger $trigger
}
else
{
    Write-Output "Scheduled task '$taskName' was found."
}


# Write-Output "--- Completed Scheduled Tasks ---"
Write-ColorOutput green "--- Completed Scheduled Tasks ---"
