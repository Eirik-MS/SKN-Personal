param (
    [string]$PythonScriptPath
)

Invoke-Expression "clear"
Write-Host "Running SKN script with python 3.11"
Invoke-Expression "py -3.11 $PythonScriptPath"
