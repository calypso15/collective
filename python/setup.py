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
    vcloud_files.download_files(config['Vcloud']['Url'], config['Vcloud']['Username'], config['Vcloud']['Password'])

    make_dir(os.path.join(HOME, 'Desktop/Malware'))
    print('Excluding malware directory from Windows Defender...')
    run_powershell('Set-MpPreference -ExclusionPath $HOME/Desktop/Malware')

    manifest = {}
    with open(os.path.join(DOWNLOAD_DIR, 'manifest.json')) as f:
        manifest = json.loads(f.read())

    print('Starting VMWare...')
    subprocess.Popen(VMWARE_PATH, shell=True)

    user32 = ctypes.WinDLL('user32')
    rv = user32.MessageBoxW
    (
        0,
        "VMWare should now be running. Please configure your license and then click OK.",
        "Starting VMWare Workstation",
        0x1 ^ 0x40 ^ 0x1000
    )

    if (rv != 1):
        print('Aborting setup.')
        sys.exit()

    print('Configuring vmnet...')
    subprocess.run(f'"{VMNETLIB64_PATH}" -- set vnet vmnet8 addr 192.168.192.0', shell=True)
    subprocess.run(f'"{VMNETLIB64_PATH}" -- set nat vmnet8 dnsautodetect 0', shell=True)
    subprocess.run(f'"{VMNETLIB64_PATH}" -- set nat vmnet8 dnsserver1 8.8.8.8', shell=True)
    subprocess.run(f'"{VMNETLIB64_PATH}" -- set nat vmnet8 dnsserver2 8.8.4.4', shell=True)

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

    print('Installing new VMs...')
    for file in sorted_list:
        name = file['name']
        install = file['import']

        if install:
            full_name = os.path.join(DOWNLOAD_DIR, name)
            print(f'Installing {full_name}...')
            subprocess.run(
                f'"{OVFTOOL_PATH}" --allowExtraConfig --net:"custom=vmnet8" -o "{full_name}" "{VM_DIR}"', shell=True)

    print('Starting VMs...')
    for file in sorted_list:
        full_name = os.path.join(VM_DIR, os.path.splitext(file['name'])[0], file['name'])

        print(f'Starting {full_name}...')
        subprocess.run(f'"{VMRUN_PATH}" -T ws start "{full_name}"', shell=True)

        p = subprocess.run(f'"{VMRUN_PATH}" -T ws getGuestIPAddress "{full_name}" -wait', shell=True, capture_output=True)
        print(f'...Machine is up with IP address {p.stdout.decode().rstrip()}')

        print(f'Disabling shared folders for {full_name}...')
        subprocess.run(f'"{VMRUN_PATH}" -T ws disableSharedFolders "{full_name}"', shell=True)
