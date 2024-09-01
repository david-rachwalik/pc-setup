# -------- Run with PowerShell (as Administrator) --------
# https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/reg-add

# Disable "Show more options" context menu in Windows 11 (right click shows full context by default)
# https://www.elevenforum.com/t/disable-show-more-options-context-menu-in-windows-11.1589
reg add "HKCU\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32" /f /ve


# Restart Windows Explorer (will restart automatically)
# https://technoresult.com/how-to-restart-windows-explorer-using-powershell
# Stop-Process -Name "explorer" -Force


Write-Host "--- Completed updates to system registry ---" -ForegroundColor Green
