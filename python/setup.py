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
    system_requirements.check_requirements()
    # vcloud_files.download_files()

    make_dirs()

    print('Excluding malware directory from Windows Defender...')
    run_powershell('Set-MpPreference -ExclusionPath $HOME/Desktop/Malware')

    print('Configuring vmnet...')
    subprocess.call(['C:/Program Files (x86)/VMware/VMware Workstation/vnetlib64.exe', '--', 'set vnet vmnet8 addr 192.168.192.0'])