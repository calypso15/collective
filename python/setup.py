import argparse
import glob
import json
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
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file')
    args = parser.parse_args()

    config = {}
    config_file = args.config_file
    with open(config_file) as f:
        config = json.loads(f.read())

    HOME = os.path.expanduser('~')
    DOWNLOAD_DIR = os.path.join(HOME, 'Documents', '.vcloud')
    VM_DIR = os.path.join(HOME, 'Documents/Virtual Machines/S1')
    VMNETLIB64_PATH = r"C:/Program Files (x86)/VMware/VMware Workstation/vnetlib64.exe"
    VMRUN_PATH = r"C:/Program Files (x86)/VMware/VMware Workstation/vmrun.exe"
    VMWARE_PATH = r"C:/Program Files (x86)/VMware/VMware Workstation/vmware.exe"
    OVFTOOL_PATH = r"C:/Program Files (x86)/VMware/VMware Workstation/OVFTool/ovftool.exe"

    system_requirements.check_requirements()
    vcloud_files.download_files(config['Vcloud']['Url'], config['Vcloud']['Username'], config['Vcloud']['Password'])

    make_dirs()

    manifest = {}
    with open(os.path.join(DOWNLOAD_DIR, 'manifest.json')) as f:
        manifest = json.loads(f.read())

    print('Excluding malware directory from Windows Defender...')
    run_powershell('Set-MpPreference -ExclusionPath $HOME/Desktop/Malware')

    print('Starting VMWare...')
    subprocess.Popen(VMWARE_PATH, shell=True)
    input('VMWare should now be running. Please configure your license and then press Enter to continue...')

    print('Configuring vmnet...')
    subprocess.run(f'"{VMNETLIB64_PATH}" -- set vnet vmnet8 addr 192.168.192.0', shell=True)
    subprocess.run(f'"{VMNETLIB64_PATH}" -- set vnet vmnet8 dnsserver1 8.8.8.8', shell=True)
    subprocess.run(f'"{VMNETLIB64_PATH}" -- set vnet vmnet8 dnsserver1 8.8.4.4', shell=True)

    print('Deleting .lck directories...')
    files = glob.glob(os.path.join(VM_DIR, '**/*.lck'), recursive=True)
    for file in files:
        print(f'Deleting {file}...')
        os.rmdir(file)

    print('Deleting old VMs...')
    files = glob.glob(os.path.join(VM_DIR, '**/*.vmx'), recursive=True)
    for file in files:
        print(f'Stopping {file}...')
        subprocess.run(f'"{VMRUN_PATH}" -T ws stop "{file}" hard', shell=True)

        print(f'Deleting {file}...')
        subprocess.run(f'"{VMRUN_PATH}" -T ws deleteVM "{file}"', shell=True)

    print('Installing new VMs...')
    for file in manifest['files']:
        name = file['name']
        install = file['import']

        if install:
            full_name = os.path.join(DOWNLOAD_DIR, name)
            print(f'Installing {full_name}...')
            subprocess.run(
                f'"{OVFTOOL_PATH}" --allowExtraConfig --net:"custom=vmnet8" -o "{full_name}" "{VM_DIR}"', shell=True)

    print('Starting VMs...')
    files = glob.glob(os.path.join(VM_DIR, '**/*.vmx'), recursive=True)
    for file in files:
        print(f'Starting {file}...')
        subprocess.run(f'"{VMRUN_PATH}" -T ws start "{file}"', shell=True)

        p = subprocess.run(f'"{VMRUN_PATH}" -T ws getGuestIPAddress "{file}" -wait', shell=True, capture_output=True)
        print(f'...Machine is up with IP address {p.stdout.decode().rstrip()}')

        print(f'Disabling shared folders for {file}...')
        subprocess.run(f'"{VMRUN_PATH}" -T ws disableSharedFolders "{file}"', shell=True)
