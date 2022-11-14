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

    print('Starting VMs...')
    files = glob.glob(os.path.join(home, 'Documents/Virtual Machines/S1', '**/*.vmx'), recursive=True)
    for file in files:
        print(f'Starting {file}...')
        subprocess.call(['C:/Program Files (x86)/VMware/VMware Workstation/vmrun', '-T ws', 'start', file])

        ip = subprocess.check_output(['C:/Program Files (x86)/VMware/VMware Workstation/vmrun', '-T ws', f'getGuestIPAddress {file}', '-wait'])
        print(f'...Machine is up with IP address {ip}')

        print(f'Disabling shared folders for {file}...')
        subprocess.call(['C:/Program Files (x86)/VMware/VMware Workstation/vmrun', '-T ws', f'disableSharedFolders {file}'])

    exit()

    system_requirements.check_requirements()
    # vcloud_files.download_files()

    make_dirs()

    print('Excluding malware directory from Windows Defender...')
    run_powershell('Set-MpPreference -ExclusionPath $HOME/Desktop/Malware')

    print('Configuring vmnet...')
    subprocess.call(['C:/Program Files (x86)/VMware/VMware Workstation/vnetlib64.exe', '--', 'set vnet vmnet8 addr 192.168.192.0'])

    print('Deleting old VMs...')
    files = glob.glob(os.path.join(home, 'Documents/Virtual Machines/S1', '**/*.vmx'), recursive=True)
    for file in files:
        print(f'Stopping {file}...')
        subprocess.call(['C:/Program Files (x86)/VMware/VMware Workstation/vmrun', '-T ws', f'stop {file}', 'hard'])

        print(f'Deleting {file}...')
        subprocess.call(['C:/Program Files (x86)/VMware/VMware Workstation/vmrun', '-T ws', f'deleteVM {file}'])

    print('Installing new VMs...')
    files = glob.glob(os.path.join(home, 'Documents/.vcloud', '**/*.ova'), recursive=True)
    for file in files:
        print(f'Installing {file}...')
        subprocess.call(['C:/Program Files (x86)/VMware/VMware Workstation/OVFTool/ovftool', '--allowExtraConfig', '--net:"custom=vmnet8"', f'-o', file, os.path.join(home, 'Documents/Virtual Machines/S1')])

    print('Starting VMs...')
    files = glob.glob(os.path.join(home, 'Documents/Virtual Machines/S1', '**/*.vmx'), recursive=True)
    for file in files:
        print(f'Starting {file}...')
        subprocess.call(['C:/Program Files (x86)/VMware/VMware Workstation/vmrun', '-T ws', f'start {file}'])

        ip = subprocess.check_output(['C:/Program Files (x86)/VMware/VMware Workstation/vmrun', '-T ws', f'getGuestIPAddress {file}', '-wait'])
        print(f'...Machine is up with IP address {ip}')

        print(f'Disabling shared folders for {file}...')
        subprocess.call(['C:/Program Files (x86)/VMware/VMware Workstation/vmrun', '-T ws', f'disableSharedFolders {file}'])
