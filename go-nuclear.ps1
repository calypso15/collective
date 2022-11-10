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

# Install other chocolatey packages
Set-Location $HOME/Documents/go-nuclear/choco

Write-Host('Installing chocolatey packages...')
Invoke-Command -ScriptBlock {
    choco install packages.config --yes
}

# Start python script
Set-Location $HOME/Documents/go-nuclear/python
pip install -r requirements.txt
python check-requirements.py
Write-Host('')

python download-files.py
Write-Host('')

if($LastExitCode -ne 0) {
    throw 'System requirements check failed, aborting.'
}

Write-Host('Creating VM directory...')
$null = New-Item -Path $HOME/Documents/VirtualMachines/S1 -ItemType Directory -Force

Write-Host('Creating malware directory...')
$null = New-Item -Path $HOME/Desktop/Malware -ItemType Directory -Force

Write-Host('Excluding malware directory from Windows Defender...')
Set-MpPreference -ExclusionPath $HOME/Desktop/Malware

vnetlib64 -- set vnet vmnet8 addr 192.168.192.0

ovftool --allowExtraConfig -o $HOME/Downloads/vcloud/TheBorg-001.ova "$HOME/Documents/Virtual Machines/S1"
vmrun -T ws start "$HOME/Documents/Virtual Machines/S1/TheBorg 001/TheBorg 001.vmx"
ovftool --allowExtraConfig -o $HOME/Downloads/vcloud/TheEnterpriseX64-002.ova "$HOME/Documents/Virtual Machines/S1"
vmrun -T ws start "$HOME/Documents/Virtual Machines/S1/TheEnterpriseX64 002/TheEnterpriseX64 002.vmx"
ovftool --allowExtraConfig -o $HOME/Downloads/vcloud/TheMelbourneX64-003.ova "$HOME/Documents/Virtual Machines/S1"
vmrun -T ws start "$HOME/Documents/Virtual Machines/S1/TheMelbourneX64 003/TheMelbourneX64 003.vmx"
ovftool --allowExtraConfig -o $HOME/Downloads/vcloud/TheSaratogaX86-004.ova "$HOME/Documents/Virtual Machines/S1"
vmrun -T ws start "$HOME/Documents/Virtual Machines/S1/TheSaratogaX86 004/TheSaratogaX86 004.vmx"