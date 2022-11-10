
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
$null = New-Item -Path "$HOME/Documents/Virtual Machines/S1" -ItemType Directory -Force

Write-Host('Creating malware directory...')
$null = New-Item -Path $HOME/Desktop/Malware -ItemType Directory -Force

Write-Host('Excluding malware directory from Windows Defender...')
Set-MpPreference -ExclusionPath $HOME/Desktop/Malware

# Set up vmnet8
Set-Location "C:/Program Files (x86)/VMware/VMware Workstation"
./vnetlib64 -- set vnet vmnet8 addr 192.168.192.0

# Delete existing VMs
Write-Host('Deleting old VMs...')
Set-Location "$HOME/Documents/Virtual Machines/S1"
$files = Get-ChildItem -Recurse -File -Filter *.vmx
Set-Location "C:/Program Files (x86)/VMware/VMware Workstation"
foreach($file in $files)
{
    Write-Host("Deleting $($file.FullName)")
    ./vmrun -T ws stop $file.FullName hard
    ./vmrun -T ws deleteVM $file.FullName
}

# Install VMs
Write-Host('Installing new VMs...')
Set-Location "C:/Program Files (x86)/VMware/VMware Workstation/OVFTool"
Get-ChildItem "$HOME/Downloads/vcloud" -Recurse -File -Filter *.ova |
Foreach-Object {
    ./ovftool --allowExtraConfig --net:"custom=vmnet8" -o $_.FullName "$HOME/Documents/Virtual Machines/S1"
}

# Start VMs
Write-Host('Starting VMs...')
Set-Location "C:/Program Files (x86)/VMware/VMware Workstation"
Get-ChildItem "$HOME/Documents/Virtual Machines/S1" -Recurse -File -Filter *.vmx |
Foreach-Object {
    ./vmrun -T ws start $_.FullName
}