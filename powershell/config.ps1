[CmdletBinding()]
param (
    [Parameter()]
    [string]
    $ConfigFile
)

Write-Host("Attempting to create file '$ConfigFile'.")