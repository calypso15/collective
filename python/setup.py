import argparse
import atexit
import ctypes
import datetime
import glob
import json
import os
import shutil
import subprocess
import sys
import winreg

import vcloud_files
import system_requirements


class Tee(object):
    def __init__(self, *files):
        self.files = files

    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush()

    def flush(self):
        for f in self.files:
            f.flush()


def make_dir(name):
    print(f'Creating directory {name}...')
    os.makedirs(name, exist_ok=True)


def run_powershell(cmd):
    completed = subprocess.run(["powershell", "-Command", cmd], capture_output=True)
    return completed


def print_header(file):
    print('**********************', file=file)
    print('Python transcript start', file=file)
    print('Start time: '+datetime.datetime.today().strftime('%Y%m%d%H%M%S'), file=file)
    print('Python version: '+sys.version, file=file)
    print('**********************', file=file)


def print_footer(file):
    print('**********************', file=file)
    print('Python transcript end', file=file)
    print('End time: '+datetime.datetime.today().strftime('%Y%m%d%H%M%S'), file=file)
    print('**********************', file=file)


if __name__ == '__main__':
    HOME = os.path.expanduser('~')
    DOCUMENTS_DIR = os.path.join(HOME, 'Documents')
    DOWNLOAD_DIR = os.path.join(DOCUMENTS_DIR, '.vcloud')
    VM_DIR = os.path.join(HOME, 'Documents/Virtual Machines/S1')
    VMWARE_DATA_DIR = r"C:/ProgramData/VMware"
    VMNETLIB64_PATH = r"C:/Program Files (x86)/VMware/VMware Workstation/vnetlib64.exe"
    VMRUN_PATH = r"C:/Program Files (x86)/VMware/VMware Workstation/vmrun.exe"
    VMWARE_PATH = r"C:/Program Files (x86)/VMware/VMware Workstation/vmware.exe"

    OVFTOOL_PATH = r"C:/Program Files (x86)/VMware/VMware Workstation/OVFTool/ovftool.exe"

    f = open(os.path.join(DOCUMENTS_DIR, 'log-python.txt'), 'a')
    sys.stdout = Tee(sys.stdout, f)
    sys.stderr = Tee(sys.stderr, f)

    print_header(f)
    atexit.register(print_footer, f)

    parser = argparse.ArgumentParser()
    parser.add_argument('config_file')
    args = parser.parse_args()

    config = {}
    config_file = args.config_file
    with open(config_file) as f:
        config = json.loads(f.read())

    system_requirements.check_requirements(ignore_warnings=config.get('IgnoreWarnings', False))

    print('Starting VMWare...')
    subprocess.Popen(VMWARE_PATH, shell=True)

    rv = ctypes.windll.user32.MessageBoxW(0, "VMWare should now be running. Please configure your license and then click OK.", "Starting VMWare Workstation", 0x1 ^ 0x40 ^ 0x1000)

    if (rv != 1):
        print('Aborting setup.')
        sys.exit()

    print('Configuring vmnet8...')
    old_lines = []
    with open(os.path.join(VMWARE_DATA_DIR, 'vmnetnat.conf'), 'r') as f:
        old_lines = f.readlines()

    new_lines = []
    for l in old_lines:
        if l.startswith('ip ='):
            new_lines.append('ip = 192.168.192.2\n')
        else:
            new_lines.append(l)

    with open(os.path.join(VMWARE_DATA_DIR, 'vmnetnat.conf'), 'w') as f:
        f.writelines(new_lines)

    registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\\WOW6432Node\\VMware, Inc.\\VMnetLib\\VMnetConfig\\vmnet8', 0, winreg.KEY_ALL_ACCESS)
    winreg.SetValueEx(registry_key, 'IPSubnetAddress', 0, winreg.REG_SZ, '192.168.192.0')
    winreg.CloseKey(registry_key)

    subprocess.run(f'"{VMNETLIB64_PATH}" -- stop nat', shell=True)
    subprocess.run(f'"{VMNETLIB64_PATH}" -- stop dhcp', shell=True)
    subprocess.run(f'"{VMNETLIB64_PATH}" -- start dhcp', shell=True)
    subprocess.run(f'"{VMNETLIB64_PATH}" -- start nat', shell=True)

    vcloud_files.download_files(config['Vcloud']['Url'], config['Vcloud']['Username'], config['Vcloud']['Password'])

    make_dir(os.path.join(HOME, 'Desktop/Malware'))
    print('Excluding malware directory from Windows Defender...')
    run_powershell('Set-MpPreference -ExclusionPath $HOME/Desktop/Malware')

    manifest = {}
    with open(os.path.join(DOWNLOAD_DIR, 'manifest.json')) as f:
        manifest = json.loads(f.read())

    if os.path.exists(VM_DIR):
        print('Stopping VMs...')
        files = glob.glob(os.path.join(VM_DIR, '**/*.vmx'), recursive=True)
        for file in files:
            print(f'Stopping {file}...')
            subprocess.run(f'"{VMRUN_PATH}" -T ws stop "{file}" hard', shell=True)

        print('Deleting old VMs...')
        shutil.rmtree(VM_DIR)

    make_dir(VM_DIR)

    sorted_list = sorted(manifest['files'], key=lambda d: d.get('order', sys.maxsize))

    print('Installing and starting new VMs...')
    for file in sorted_list:
        name = file['name']
        base_name = os.path.splitext(name)[0]
        install = file['import']

        ova_path = os.path.join(DOWNLOAD_DIR, name)
        vmx_path = os.path.join(VM_DIR, base_name, base_name+'.vmx')

        if install:
            print(f'Installing {ova_path}...')
            subprocess.run(
                f'"{OVFTOOL_PATH}" --allowExtraConfig --net:"custom=vmnet8" -o "{ova_path}" "{VM_DIR}"', shell=True)

            print(f'Starting {vmx_path}...')
            subprocess.run(f'"{VMRUN_PATH}" -T ws start "{vmx_path}"', shell=True)

            p = subprocess.run(f'"{VMRUN_PATH}" -T ws getGuestIPAddress "{vmx_path}" -wait',
                            shell=True, capture_output=True)
            print(f'...Machine is up with IP address {p.stdout.decode().rstrip()}')

            print(f'Disabling shared folders for {vmx_path}...')
            subprocess.run(f'"{VMRUN_PATH}" -T ws disableSharedFolders "{vmx_path}"', shell=True)
