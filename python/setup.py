import argparse
import atexit
import ctypes
import datetime
import glob
import json
import os
import platform
import requests
import shutil
import subprocess
import sys
import time
import tkinter
import traceback
import winreg
import wmi

from tkinter import messagebox
from tkinter import simpledialog

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


HOME = os.path.expanduser("~")
DOCUMENTS_DIR = os.path.join(HOME, "Documents")
DOWNLOAD_DIR = os.path.join(DOCUMENTS_DIR, ".vcloud")
VM_DIR = os.path.join(HOME, "Documents\\Virtual Machines\\S1")
PROGRAM_FILES_DIR = "C:\\Program Files (x86)"
VMWARE_DATA_DIR = "C:\\ProgramData\\VMware"
VMWARE_WORKSTATION_DIR = os.path.join(PROGRAM_FILES_DIR, "VMware\\VMware Workstation")
VMNETLIB64_PATH = os.path.join(VMWARE_WORKSTATION_DIR, "vnetlib64.exe")
VMRUN_PATH = os.path.join(VMWARE_WORKSTATION_DIR, "vmrun.exe")
VMWARE_PATH = os.path.join(VMWARE_WORKSTATION_DIR, "vmware.exe")
OVFTOOL_PATH = os.path.join(VMWARE_WORKSTATION_DIR, "OVFTool\\ovftool.exe")


def main():
    f = open(os.path.join(DOCUMENTS_DIR, "log-python.txt"), "a")
    sys.stdout = Tee(sys.stdout, f)
    sys.stderr = Tee(sys.stderr, f)

    print_header(f)
    atexit.register(print_footer, f)

    parser = argparse.ArgumentParser()
    parser.add_argument("config_file")
    args = parser.parse_args()

    global config
    config = {}
    config_file = args.config_file
    print(f"Trying to open json file: {config_file}")
    with open(config_file) as f:
        config = json.loads(f.read())

    system_requirements.check_requirements(
        ignore_warnings=config.get("IgnoreWarnings", False),
        ignore_errors=config.get("IgnoreErrors", False),
    )

    root = tkinter.Tk()
    root.attributes("-topmost", True)
    root.attributes("-toolwindow", True)
    root.geometry(
        "1x1+{}+{}".format(
            int(root.winfo_screenwidth() / 2), int(root.winfo_screenheight() / 2)
        )
    )
    root.overrideredirect(1)
    root.update_idletasks()

    interactive = not config.get("NonInteractive", False)
    sitetoken = config.get("SiteToken", None)

    print("Starting VMWare...")
    subprocess.Popen(VMWARE_PATH, shell=True)

    if interactive:
        ready = messagebox.askokcancel(
            title="Starting VMWare Workstation",
            message="VMWare should now be running. Please configure your license and then click OK.",
            icon=messagebox.INFO,
            parent=root,
        )

        if not ready:
            print("Aborting setup.")
            sys.exit()

    make_dir(os.path.join(HOME, "Desktop/Malware"))
    print("Excluding malware directory from Windows Defender.")
    run_powershell("Set-MpPreference -ExclusionPath $HOME/Desktop/Malware")

    global AUTH, VCLOUD_URL
    AUTH = None
    VCLOUD_URL = config["Vcloud"]["Url"]

    try:
        AUTH = requests.auth.HTTPBasicAuth(
            config["Vcloud"]["Username"], config["Vcloud"]["Password"]
        )
        r = requests.get(VCLOUD_URL, auth=AUTH)
        r.raise_for_status()
    except requests.ConnectionError as x:
        print(traceback.format_exc())
        print(
            f"Unable to connect to {VCLOUD_URL}, exiting. Please contact ryan.ogrady@sentinelone.com for additional support."
        )
        sys.exit()
    except requests.HTTPError as x:
        print(traceback.format_exc())
        print(
            f"Received HTTP {x.response.status_code}, exiting. Please contact ryan.ogrady@sentinelone.com for additional support."
        )
        sys.exit()

    vcloud_files.download_files(url=VCLOUD_URL, auth=AUTH, interactive=interactive)

    install = True
    if interactive:
        install = messagebox.askyesno(
            title="Install virtual environment?",
            message="Do you want to install the virtual environment? This will delete the old environment (if any), and you will need to re-install agents, snapshots, etc.",
            icon=messagebox.WARNING,
            parent=root,
        )

    if install:
        if interactive:
            sitetoken = simpledialog.askstring(
                title="Install EDR agent?",
                prompt="Enter a site or group token to automatically install the EDR agent.",
                initialvalue=sitetoken,
                parent=root,
            )

        print("Configuring vmnet8.")
        old_lines = []
        with open(os.path.join(VMWARE_DATA_DIR, "vmnetnat.conf"), "r") as f:
            old_lines = f.readlines()

        new_lines = []
        for l in old_lines:
            if l.startswith("ip ="):
                new_lines.append("ip = 192.168.192.2/24\n")
            else:
                new_lines.append(l)

        with open(os.path.join(VMWARE_DATA_DIR, "vmnetnat.conf"), "w") as f:
            f.writelines(new_lines)

        registry_key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\\WOW6432Node\\VMware, Inc.\\VMnetLib\\VMnetConfig\\vmnet8",
            0,
            winreg.KEY_ALL_ACCESS,
        )
        winreg.SetValueEx(
            registry_key, "IPSubnetAddress", 0, winreg.REG_SZ, "192.168.192.0"
        )
        winreg.CloseKey(registry_key)

        subprocess.run(f'"{VMNETLIB64_PATH}" -- stop nat', shell=True)
        subprocess.run(f'"{VMNETLIB64_PATH}" -- stop dhcp', shell=True)
        subprocess.run(f'"{VMNETLIB64_PATH}" -- start dhcp', shell=True)
        subprocess.run(f'"{VMNETLIB64_PATH}" -- start nat', shell=True)

        manifest = None
        if os.path.exists(os.path.join(DOWNLOAD_DIR, "manifest.json")):
            with open(os.path.join(DOWNLOAD_DIR, "manifest.json")) as f:
                manifest = json.loads(f.read())

        if manifest != None:
            if os.path.exists(VM_DIR):
                print("Stopping VMs...")
                files = glob.glob(os.path.join(VM_DIR, "**/*.vmx"), recursive=True)
                for file in files:
                    print(f"...Stopping {file}.")
                    subprocess.run(
                        f'"{VMRUN_PATH}" -T ws stop "{file}" hard', shell=True
                    )

                print("Deleting old VMs.")
                shutil.rmtree(VM_DIR, ignore_errors=True)

            print("Installing new environment...")
            make_dir(VM_DIR)

            install_list = []
            for file in manifest["files"]:
                if file["import"]:
                    item = {}
                    base_name = os.path.splitext(file["name"])[0]
                    item["name"] = file["name"]
                    item["order"] = file.get("order", sys.maxsize)
                    item["ova_path"] = os.path.join(DOWNLOAD_DIR, file["name"])
                    item["vmx_path"] = os.path.join(
                        VM_DIR, base_name, base_name + ".vmx"
                    )
                    install_list.append(item)

            for file in sorted(install_list, key=lambda x: x["order"]):
                vmx_path = file["vmx_path"]
                ova_path = file["ova_path"]
                print(f"Installing {vmx_path}...")
                install_vm(ova_path, vmx_path)

            for file in sorted(install_list, key=lambda x: x["order"]):
                vmx_path = file["vmx_path"]
                print(f"Setting up {vmx_path}...")
                setup_vm(vmx_path)

                if sitetoken != None:
                    install_agent(vmx_path, sitetoken)

            print(f"Preparing to take snapshots...")
            for file in sorted(install_list, key=lambda x: x["order"]):
                vmx_path = file["vmx_path"]
                wait_until_online(vmx_path)

            for file in sorted(install_list, key=lambda x: x["order"]):
                vmx_path = file["vmx_path"]
                print(f"Creating snapshot 'Baseline' for {vmx_path}...")
                create_snapshot(vmx_path, "Baseline")

        else:
            print("Skipping environment setup, there was a problem with the manifest.")
    else:
        print("Skipping environment setup at user request.")

    root.destroy()


def install_vm(ova_path, vmx_path):
    print(f"...Importing {ova_path}.")
    subprocess.run(
        f'"{OVFTOOL_PATH}" --allowExtraConfig --net:"custom=vmnet8" -o "{ova_path}" "{VM_DIR}"'
    )

    print(f"...Starting {vmx_path}.")
    subprocess.run(f'"{VMRUN_PATH}" -T ws start "{vmx_path}"', shell=True)

    ip = get_ip_address(vmx_path)
    print(f"...Machine is up with IP address {ip}.")


def setup_vm(vmx_path):
    username = "STARFLEET\jeanluc"
    password = "Sentinelone!"
    restart_required = False

    ip = get_ip_address(vmx_path)

    if ip in ("192.168.192.10", "192.168.192.20", "192.168.192.21", "192.168.192.22"):
        wait_until_online(vmx_path)
        print(f"...Re-arming license.")
        run_script(
            vmx_path=vmx_path,
            username=username,
            password=password,
            script=(f"cscript.exe C:\Windows\system32\slmgr.vbs /rearm"),
        )

        restart_required = True

    if ip == "192.168.192.10":
        identifier = get_identifier()
        identifier = convert_hex_to_base36(identifier)

        wait_until_online(vmx_path)
        print(f"...Renaming Windows VMs with suffix '-{identifier}'.")
        run_script(
            vmx_path=vmx_path,
            username=username,
            password=password,
            script=(
                f"netdom computername 192.168.192.10 /add:TheBorg-{identifier}.starfleet.corp"
                f' & netdom renamecomputer 192.168.192.20 /newname:Enterprise-{identifier} /userd:"{username}" /passwordd:"{password}" /force /reboot 0'
                f' & netdom renamecomputer 192.168.192.21 /newname:Melbourne-{identifier} /userd:"{username}" /passwordd:"{password}" /force /reboot 0'
                f' & netdom renamecomputer 192.168.192.22 /newname:Saratoga-{identifier} /userd:"{username}" /passwordd:"{password}" /force /reboot 0'
                f" & netdom computername 192.168.192.10 /makeprimary:TheBorg-{identifier}.starfleet.corp"
            ),
        )

    if restart_required:
        restart(vmx_path)
        wait_until_online(vmx_path)

        print(f"...Restarting explorer.exe.")
        run_script(
            vmx_path=vmx_path,
            username=username,
            password=password,
            script=(f"taskkill /f /im explorer.exe && start explorer.exe"),
        )
        restart_required = False

    print(f"...Disabling sound card.")
    subprocess.run(
        f'"{VMRUN_PATH}" -T ws disconnectNamedDevice "{vmx_path}" "sound"', shell=True
    )

    print(f"...Disabling shared folders.")
    subprocess.run(
        f'"{VMRUN_PATH}" -T ws disableSharedFolders "{vmx_path}"', shell=True
    )


def install_agent(vmx_path, site_token):
    username = "STARFLEET\jeanluc"
    password = "Sentinelone!"

    ip = get_ip_address(vmx_path)

    if ip in ("192.168.192.10", "192.168.192.20", "192.168.192.21"):
        wait_until_online(vmx_path)
        print(f"...Installing agent with site token '{site_token}'.")
        run_script(
            vmx_path=vmx_path,
            username=username,
            password=password,
            script=(
                f'SCHTASKS /create /tn Agent /sc once /tr ""msiexec /passive /i ""C:\\Users\\jeanluc\\Desktop\\SentinelInstaller_windows_64bit.msi"" SITE_TOKEN={site_token}"" /ru interactive /rl highest /st 00:00 /f && SCHTASKS /run /tn Agent && SCHTASKS /delete /tn Agent /f'
            ),
        )

    if ip in ("192.168.192.22"):
        wait_until_online(vmx_path)
        print(f"...Installing agent with site token '{site_token}'.")
        run_script(
            vmx_path=vmx_path,
            username=username,
            password=password,
            script=(
                f'SCHTASKS /create /tn Agent /sc once /tr ""msiexec /passive /i ""C:\\Users\\jeanluc\\Desktop\\SentinelInstaller_windows_32bit.msi"" SITE_TOKEN={site_token}"" /ru interactive /rl highest /st 00:00 /f && SCHTASKS /run /tn Agent && SCHTASKS /delete /tn Agent /f'
            ),
        )


def create_snapshot(vmx_path, name):
    subprocess.run(f'"{VMRUN_PATH}" -T ws snapshot "{vmx_path}" "{name}"', shell=True)


def restart(vmx_path):
    print(f"...Issuing restart.")
    subprocess.run(
        f'"{VMRUN_PATH}" -T ws reset "{vmx_path}" soft',
        shell=True,
        capture_output=True,
    )


def wait_until_online(vmx_path):
    username = "STARFLEET\jeanluc"
    password = "Sentinelone!"
    print(f"...Waiting for machine to be ready...")
    subprocess.run(
        f'"{VMRUN_PATH}" -T ws -gu "{username}" -gp "{password}" runProgramInGuest "{vmx_path}" "C:\Windows\System32\whoami.exe"',
        shell=True,
        capture_output=True,
    )
    time.sleep(5)


def get_ip_address(vmx_path):
    p = subprocess.run(
        f'"{VMRUN_PATH}" -T ws getGuestIPAddress "{vmx_path}" -wait',
        shell=True,
        capture_output=True,
    )
    return p.stdout.decode().rstrip()


def run_script(vmx_path, username, password, script, interpreter=""):
    full_script = f'"{VMRUN_PATH}" -T ws -gu "{username}" -gp "{password}" runScriptInGuest "{vmx_path}" "{interpreter}" "{script}"'
    #   print(f"...Running subprocess: {full_script}")
    p = subprocess.run(
        full_script,
        shell=True,
        capture_output=True,
    )

    return p.stdout.decode().rstrip()


def get_identifier():
    try:
        # Create a new WMI instance
        c = wmi.WMI()
        # Get the machine UUID
        uuid = c.Win32_ComputerSystemProduct()[0].UUID
        # Get the last 5 characters of the UUID
        return uuid[-5:]
    except Exception as e:
        print(f"Failed to get the last 5 characters of the machine UUID. Error: {e}")
        sys.exit(1)


def convert_hex_to_base36(hex_string):
    base36_chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    decimal = int(hex_string, 16)
    base36_string = ""

    while decimal > 0:
        remainder = decimal % 36
        base36_string = base36_chars[remainder] + base36_string
        decimal = decimal // 36

    return base36_string


def make_dir(name):
    print(f"...Creating directory {name}")
    os.makedirs(name, exist_ok=True)


def run_powershell(cmd):
    completed = subprocess.run(["powershell", "-Command", cmd], capture_output=True)
    return completed


def print_header(file):
    print("**********************", file=file)
    print("Python transcript start", file=file)
    print(
        "Start time: " + datetime.datetime.today().strftime("%Y%m%d%H%M%S"), file=file
    )
    print("Python version: " + sys.version, file=file)
    print("**********************", file=file)


def print_footer(file):
    print("**********************", file=file)
    print("Python transcript end", file=file)
    print("End time: " + datetime.datetime.today().strftime("%Y%m%d%H%M%S"), file=file)
    print("**********************", file=file)


if __name__ == "__main__":
    main()
