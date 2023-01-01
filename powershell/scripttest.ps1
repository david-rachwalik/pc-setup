# https://stackoverflow.com/questions/6816450/call-powershell-script-ps1-from-another-ps1-script-inside-powershell-ise

Write-Host "InvocationName: " + $MyInvocation.InvocationName
Write-Host "Path: " + $MyInvocation.MyCommand.Path

Write-Host "Script: " + $PSCommandPath
Write-Host "Path: " + $PSScriptRoot
