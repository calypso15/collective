# Update environment variables
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Install chocolatey
if ((Get-Command 'choco.exe' -ErrorAction SilentlyContinue) -eq $null) {
    Write-Host('Installing chocolatey...')
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

    if ((Get-Command 'choco.exe' -ErrorAction SilentlyContinue) -eq $null) {
        throw 'Failed to install chocolatey, aborting.'
    }
}

# Install git
if ((Get-Command 'git.exe' -ErrorAction SilentlyContinue) -eq $null) {
    Write-Host('Installing git...')
    Invoke-Command -ScriptBlock {
        choco install git --yes
    }

    if ((Get-Command 'git.exe' -ErrorAction SilentlyContinue) -eq $null) {
        throw 'Failed to install git, aborting.'
    }
}

$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Clone the go-nuclear repo if it doesn't already exist
if (-Not (Test-Path -Path $HOME/Documents/go-nuclear)) {
    Set-Location $HOME/Documents

    Write-Host('Cloning go-nuclear repo...')
    Invoke-Command -ScriptBlock {
        git clone https://github.com/calypso15/go-nuclear.git
    }

    if (-Not (Test-Path -Path $HOME/Documents/go-nuclear)) {
        throw 'Failed to clone go-nuclear repo, aborting.'
    }
}

# Update repo
Set-Location $HOME/Documents/go-nuclear

Write-Host('Updating go-nuclear repo...')
git pull

# Check for updated script
if(Compare-Object -ReferenceObject $(Get-Content $HOME/Documents/go-nuclear/go-nuclear.ps1) -DifferenceObject $(Get-Content $MyInvocation.MyCommand.Path)) {
    Write-Host('Updating go-nuclear bootstrap script...')
    Copy-Item $HOME/Documents/go-nuclear/go-nuclear.ps1 $MyInvocation.MyCommand.Path
    &$MyInvocation.MyCommand.Path
    exit
}

& "./powershell/setup.ps1"