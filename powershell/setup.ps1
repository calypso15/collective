
# Install other chocolatey packages
Set-Location $HOME/Documents/go-nuclear/choco

Write-Host('Installing chocolatey packages...')
Invoke-Command -ScriptBlock {
    choco install packages.config --yes
}

# Start python script
Set-Location $HOME/Documents/go-nuclear/python
pip install -r requirements.txt
python setup.py
Write-Host('')

if($LastExitCode -ne 0) {
    throw 'setup.py failed, aborting.'
}

Write-Host('Creating VM directory...')
$null = New-Item -Path "$HOME/Documents/Virtual Machines/S1" -ItemType Directory -Force

Write-Host('Creating malware directory...')
$null = New-Item -Path $HOME/Desktop/Malware -ItemType Directory -Force

Write-Host('Excluding malware directory from Windows Defender...')
Set-MpPreference -ExclusionPath $HOME/Desktop/Malware

# Set up vmnet8
Set-Location "C:/Program Files (x86)/VMware/VMware Workstation"
Write-Host('Configuring vmnet8...')
./vnetlib64 -- set vnet vmnet8 addr 192.168.192.0

# Delete existing VMs
Write-Host('Deleting old VMs...')
Set-Location "$HOME/Documents/Virtual Machines/S1"
$files = Get-ChildItem -Recurse -File -Filter *.vmx | Where-Object { $_.Extension -eq '.vmx' }
Set-Location "C:/Program Files (x86)/VMware/VMware Workstation"
foreach($file in $files)
{
    Write-Host("Stopping $($file.FullName)...")
    ./vmrun -T ws stop $file.FullName hard
    Write-Host("Deleting $($file.FullName)...")
    ./vmrun -T ws deleteVM $file.FullName
}

# Install VMs
Write-Host('Installing new VMs...')
Set-Location "$HOME/Documents/.vcloud"
$files = Get-ChildItem -Recurse -File -Filter *.ova | Where-Object { $_.Extension -eq '.ova' }
Set-Location "C:/Program Files (x86)/VMware/VMware Workstation/OVFTool"
foreach($file in $files)
{
    Write-Host("Installing $($file.FullName)...")
    ./ovftool --allowExtraConfig --net:"custom=vmnet8" -o $file.FullName "$HOME/Documents/Virtual Machines/S1"
}

# Start VMs
Write-Host('Starting VMs...')
Set-Location "$HOME/Documents/Virtual Machines/S1"
$files = Get-ChildItem -Recurse -File -Filter *.vmx | Where-Object { $_.Extension -eq '.vmx' }
Set-Location "C:/Program Files (x86)/VMware/VMware Workstation"
foreach($file in $files)
{
    Write-Host("Starting $($file.FullName)...")
    ./vmrun -T ws start $file.FullName
    $ip = (./vmrun -T ws getGuestIPAddress $file.FullName -wait)
    Write-Host("...Machine is up with IP address $ip")
    Write-Host("Disabling shared folders for $($file.FullName)...")
    ./vmrun -T ws disableSharedFolders $file.FullName
}