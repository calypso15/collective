[CmdletBinding()]
param (
    [Parameter()]
    [string]
    $ConfigFile
)

Start-Transcript -Path log.txt -Append

if ('ConfigFile' -NotIn $PSBoundParameters.Keys)
{
    Write-Host 'No config file specified with the -ConfigFile parameter, aborting.'
    Exit
}

$ConfigFile = Resolve-Path $ConfigFile

# Update environment variables
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Install chocolatey
if ($null -eq (Get-Command 'choco.exe' -ErrorAction SilentlyContinue)) {
    Write-Host('Installing chocolatey...')
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1')) | Out-Host

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
    } | Out-Host

    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

    if ($null -eq (Get-Command 'git.exe' -ErrorAction SilentlyContinue)) {
        throw 'Failed to install git, aborting.'
    }
}

# Clone the go-nuclear repo if it doesn't already exist
if (-Not (Test-Path -Path $HOME/Documents/go-nuclear)) {
    Set-Location $HOME/Documents

    Write-Host('Cloning go-nuclear repo...')
    Invoke-Command -ScriptBlock {
        git clone https://github.com/calypso15/go-nuclear.git
    } | Out-Host

    if (-Not (Test-Path -Path $HOME/Documents/go-nuclear)) {
        throw 'Failed to clone go-nuclear repo, aborting.'
    }
}

# Update repo
Set-Location $HOME/Documents/go-nuclear

Write-Host('Updating go-nuclear repo...')
Invoke-Expression "git pull" | Out-Host

# Check for updated script
if(Compare-Object -ReferenceObject $(Get-Content $HOME/Documents/go-nuclear/go-nuclear.ps1) -DifferenceObject $(Get-Content $MyInvocation.MyCommand.Path)) {
    Write-Host('Updating go-nuclear bootstrap script...')
    Copy-Item $HOME/Documents/go-nuclear/go-nuclear.ps1 $MyInvocation.MyCommand.Path
    &$MyInvocation.MyCommand.Path -ConfigFile "$ConfigFile" | Out-Host
    exit
}

Set-Location $HOME/Documents/go-nuclear/powershell
Invoke-Expression "& ./setup.ps1 -ConfigFile `"$ConfigFile`"" | Out-Host