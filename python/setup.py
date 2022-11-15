import glob
import os
import subprocess

import vcloud_files
import system_requirements

def make_dir(name):
    print(f'Creating directory {name}...')
    os.makedirs(name, exist_ok=True)

def make_dirs():
    home = os.path.expanduser('~')

    make_dir(os.path.join(home, 'Documents/Virtual Machines/S1'))
    make_dir(os.path.join(home, 'Desktop/Malware'))

def run_powershell(cmd):
    completed = subprocess.run(["powershell", "-Command", cmd], capture_output=True)
    return completed

if __name__ == '__main__':
    home = os.path.expanduser('~')

    system_requirements.check_requirements()
    # vcloud_files.download_files()

    make_dirs()

    print('Excluding malware directory from Windows Defender...')
    run_powershell('Set-MpPreference -ExclusionPath $HOME/Desktop/Malware')

    print('Configuring vmnet...')
    subprocess.run(f'C:/Program Files (x86)/VMware/VMware Workstation/vnetlib64.exe -- set vnet vmnet8 addr 192.168.192.0', shell=True)

    print('Deleting old VMs...')
    files = glob.glob(os.path.join(home, 'Documents/Virtual Machines/S1', '**/*.vmx'), recursive=True)
    for file in files:
        print(f'Stopping {file}...')
        subprocess.run(f'C:/Program Files (x86)/VMware/VMware Workstation/vmrun.exe -T ws stop {file} hard', shell=True)

        print(f'Deleting {file}...')
        subprocess.run(f'C:/Program Files (x86)/VMware/VMware Workstation/vmrun.exe -T ws deleteVM {file}', shell=True)

    print('Installing new VMs...')
    files = glob.glob(os.path.join(home, 'Documents/.vcloud', '**/*.ova'), recursive=True)
    for file in files:
        print(f'Installing {file}...')
        subprocess.run(f'C:/Program Files (x86)/VMware/VMware Workstation/OVFTool/ovftool.exe --allowExtraConfig --net:"custom=vmnet8" -o {file} {os.path.join(home, "Documents/Virtual Machines/S1")}', shell=True)

    print('Starting VMs...')
    files = glob.glob(os.path.join(home, 'Documents/Virtual Machines/S1', '**/*.vmx'), recursive=True)
    for file in files:
        print(f'Starting {file}...')
        subprocess.run(f'C:/Program Files (x86)/VMware/VMware Workstation/vmrun.exe -T ws start {file}', shell=True)

        p = subprocess.run(f'C:/Program Files (x86)/VMware/VMware Workstation/vmrun.exe -T ws getGuestIPAddress {file} -wait', shell=True, capture_output=True)
        print(f'...Machine is up with IP address {p.stdout}')

        print(f'Disabling shared folders for {file}...')
        subprocess.run(f'C:/Program Files (x86)/VMware/VMware Workstation/vmrun.exe -T ws disableSharedFolders {file}', shell=True)
