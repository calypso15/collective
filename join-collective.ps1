[CmdletBinding()]
param (
    [Parameter()]
    [string]
    $ConfigFile
)

Start-Transcript -Path $HOME/Documents/log-powershell.txt -Append

if ('ConfigFile' -NotIn $PSBoundParameters.Keys)
{
    Write-Host 'No config file specified with the -ConfigFile parameter, aborting.'
    Exit
}

try
{
    $ConfigFile = Resolve-Path $ConfigFile -ErrorAction SilentlyContinue
}
catch
{
    Write-Host 'Specified config file not found, aborting.'
    Exit
}

# Update environment variables
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Install chocolatey
if ($null -eq (Get-Command 'choco.exe' -ErrorAction SilentlyContinue)) {
    Write-Host('Installing chocolatey...')
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

    if ($null -eq (Get-Command 'choco.exe' -ErrorAction SilentlyContinue)) {
        throw 'Failed to install chocolatey, aborting.'
    }
}

# Install git
if ($null -eq (Get-Command 'git.exe' -ErrorAction SilentlyContinue)) {
    Write-Host('Installing git...')
    Invoke-Command -ScriptBlock {
        choco install git --yes
    }

    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

    if ($null -eq (Get-Command 'git.exe' -ErrorAction SilentlyContinue)) {
        throw 'Failed to install git, aborting.'
    }
}

# Clone the collective repo if it doesn't already exist
if (-Not (Test-Path -Path $HOME/Documents/collective)) {
    Set-Location $HOME/Documents

    Write-Host('Cloning collective repo...')
    Invoke-Command -ScriptBlock {
        git clone https://github.com/calypso15/collective.git
    }

    if (-Not (Test-Path -Path $HOME/Documents/collective)) {
        throw 'Failed to clone collective repo, aborting.'
    }
}

# Update repo
Set-Location $HOME/Documents/collective

Write-Host('Updating collective repo...')
git pull

# Check for updated script
if(Compare-Object -ReferenceObject $(Get-Content $HOME/Documents/collective/join-collective.ps1) -DifferenceObject $(Get-Content $MyInvocation.MyCommand.Path)) {
    Write-Host('Updating collective bootstrap script...')
    Copy-Item $HOME/Documents/collective/join-collective.ps1 $MyInvocation.MyCommand.Path
    &$MyInvocation.MyCommand.Path -ConfigFile "$ConfigFile"
    exit
}

Set-Location $HOME/Documents/collective/powershell
& ./setup.ps1 -ConfigFile "$ConfigFile"