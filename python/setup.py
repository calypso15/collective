import argparse
import atexit
import datetime
import glob
import json
import logging
import os
import psutil
import requests
import shutil
import signal
import subprocess
import sys
import threading
import time
import tkinter
import traceback
import winreg
import wmi

from tkinter import messagebox
from tkinter import simpledialog

import log_config
import vcloud_files
import system_requirements

logger = logging.getLogger(__name__)

HOME = os.path.expanduser("~")
DOCUMENTS_DIR = os.path.join(HOME, R"Documents")
DOWNLOAD_DIR = os.path.join(DOCUMENTS_DIR, R".vcloud")
VM_DIR = os.path.join(HOME, R"Documents\Virtual Machines\S1")
PROGRAM_FILES_DIR = R"C:\Program Files (x86)"
VMWARE_DATA_DIR = R"C:\ProgramData\VMware"
VMWARE_WORKSTATION_DIR = os.path.join(PROGRAM_FILES_DIR, R"VMware\VMware Workstation")
VMNETLIB64_PATH = os.path.join(VMWARE_WORKSTATION_DIR, R"vnetlib64.exe")
VMRUN_PATH = os.path.join(VMWARE_WORKSTATION_DIR, R"vmrun.exe")
VMWARE_PATH = os.path.join(VMWARE_WORKSTATION_DIR, R"vmware.exe")
OVFTOOL_PATH = os.path.join(VMWARE_WORKSTATION_DIR, R"OVFTool\ovftool.exe")


def main():
    print_header()
    atexit.register(print_footer)
    signal.signal(signal.SIGINT, sigint_handler)

    parser = argparse.ArgumentParser()
    parser.add_argument("config_file")
    args = parser.parse_args()

    global config
    config = {}
    config_file = args.config_file
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

    if interactive and not is_workstation_licensed():
        logger.info("Starting VMWare Workstation...")
        subprocess.Popen(VMWARE_PATH, shell=True)

        ready = messagebox.askokcancel(
            title="Starting VMWare Workstation",
            message="VMWare should now be running. Please add a license or start the free trial, then click OK.",
            icon=messagebox.INFO,
            parent=root,
        )

        if not ready:
            logger.warning("Aborting setup at user request.")
            sys.exit(1)

    if is_workstation_licensed():
        logger.info("VMware Workstation license found.")
    else:
        logger.error(
            "VMware Workstation license not found, aborting. Please install and open VMware Workstation and add a license or start the free trial, then re-run setup."
        )
        sys.exit(1)

    make_dir(os.path.join(HOME, "Desktop/Malware"))
    logger.info("Excluding malware directory from Windows Defender.")
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
        logger.debug(traceback.format_exc())
        logger.error(
            f"Unable to connect to {VCLOUD_URL}, exiting. Please contact ryan.ogrady@sentinelone.com for additional support."
        )
        sys.exit(1)
    except requests.HTTPError as x:
        logger.debug(traceback.format_exc())
        logger.error(
            f"Received HTTP {x.response.status_code} while connecting to {VCLOUD_URL}, exiting. Please contact ryan.ogrady@sentinelone.com for additional support."
        )
        sys.exit(1)

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

    vcloud_files.download_files(url=VCLOUD_URL, auth=AUTH, interactive=interactive)

    if install:
        logger.info("Configuring vmnet8.")
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
            R"SOFTWARE\WOW6432Node\VMware, Inc.\VMnetLib\VMnetConfig\vmnet8",
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
                logger.info("Stopping VMs...")
                files = glob.glob(os.path.join(VM_DIR, "**/*.vmx"), recursive=True)
                for file in files:
                    logger.info(f"...Stopping {file}.")
                    subprocess.run(
                        f'"{VMRUN_PATH}" -T ws stop "{file}" hard', shell=True
                    )

                logger.info("Deleting old VMs.")
                shutil.rmtree(VM_DIR, ignore_errors=True)

            logger.info("Installing new environment...")
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
                logger.info(f"Installing {vmx_path}...")
                install_vm(ova_path, vmx_path)

            for file in sorted(install_list, key=lambda x: x["order"]):
                vmx_path = file["vmx_path"]
                logger.info(f"Setting up {vmx_path}...")
                setup_vm(vmx_path)

                if sitetoken != None:
                    install_agent(vmx_path, sitetoken)

            logger.info(f"Waiting for agent installation to finish...")
            time.sleep(30)

            threads = []
            logger.info(f"Taking snapshots...")
            sys.stdout.flush()
            for file in sorted(install_list, key=lambda x: x["order"]):
                vmx_path = file["vmx_path"]
                logger.info(f"Creating snapshot 'Baseline' for {vmx_path}...")
                wait_until_online(vmx_path)
                logger.info(f"...Starting snapshot...")
                sys.stdout.flush()
                thread = threading.Thread(
                    target=create_snapshot,
                    args=(vmx_path, "Baseline"),
                )
                threads.append(thread)
                thread.start()

            logger.info(f"Waiting for snapshots to finish...")
            for thread in threads:
                thread.join()
            logger.info(f"...Snapshots finished.")
        else:
            logger.error(
                "Skipping environment setup, there was a problem with the manifest."
            )
    else:
        logger.warning("Skipping environment setup at user request.")

    root.destroy()

    time.sleep(5)
    if not is_vmware_running():
        logger.info(f"Starting VMware Workstation...")
        subprocess.Popen(VMWARE_PATH, shell=True)

    logger.info(f"Setup is complete!")


def is_vmware_running():
    for process in psutil.process_iter(attrs=["pid", "name"]):
        if "vmware.exe" in process.info["name"]:
            return True
    return False


def is_workstation_licensed():
    try:
        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            R"SOFTWARE\WOW6432Node\VMware, Inc.\VMware Workstation",
        ) as key:
            index = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(key, index)

                    if "License" in subkey_name:
                        with winreg.OpenKey(key, subkey_name) as sub:
                            try:
                                winreg.QueryValueEx(sub, "Serial")
                                return True
                            except FileNotFoundError:
                                pass
                    index += 1
                except OSError:
                    break
    except FileNotFoundError as x:
        return False

    return False


def install_vm(ova_path, vmx_path):
    logger.info(f"...Importing {ova_path}.")
    subprocess.run(
        f'"{OVFTOOL_PATH}" --allowExtraConfig --net:"custom=vmnet8" -o "{ova_path}" "{VM_DIR}"'
    )

    logger.info(f"...Starting {vmx_path}.")
    subprocess.run(f'"{VMRUN_PATH}" -T ws start "{vmx_path}" nogui', shell=True)

    ip = get_ip_address(vmx_path)
    logger.info(f"...Machine is up with IP address {ip}.")


def setup_vm(vmx_path):
    # These are "known bad" credentials for use with malware sandbox VMs.
    # Do not submit as a bug bounty, it will not be awarded.
    username = R"STARFLEET\jeanluc"
    password = R"Sentinelone!"
    restart_required = False

    ip = get_ip_address(vmx_path)

    if ip in ("192.168.192.10", "192.168.192.20", "192.168.192.21", "192.168.192.22"):
        wait_until_online(vmx_path)
        logger.info(f"...Re-arming license.")
        run_script(
            vmx_path=vmx_path,
            username=username,
            password=password,
            script=(Rf"cscript.exe C:\Windows\system32\slmgr.vbs /rearm"),
        )

        restart_required = True

    if ip == "192.168.192.10":
        identifier = get_identifier()
        identifier = convert_hex_to_base36(identifier)

        wait_until_online(vmx_path)
        logger.info(f"...Renaming Windows VMs with suffix '-{identifier}'.")
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

        logger.info(f"...Restarting explorer.exe.")
        run_script(
            vmx_path=vmx_path,
            username=username,
            password=password,
            script=(f"taskkill /f /im explorer.exe && start explorer.exe"),
        )
        restart_required = False

    logger.info(f"...Disabling sound card.")
    subprocess.run(
        f'"{VMRUN_PATH}" -T ws disconnectNamedDevice "{vmx_path}" "sound"', shell=True
    )

    logger.info(f"...Disabling shared folders.")
    subprocess.run(
        f'"{VMRUN_PATH}" -T ws disableSharedFolders "{vmx_path}"', shell=True
    )


def install_agent(vmx_path, site_token):
    username = R"STARFLEET\jeanluc"
    password = R"Sentinelone!"

    ip = get_ip_address(vmx_path)

    if ip in ("192.168.192.10", "192.168.192.20", "192.168.192.21"):
        wait_until_online(vmx_path)
        logger.info(f"...Installing agent with site token '{site_token}'.")
        run_script(
            vmx_path=vmx_path,
            username=username,
            password=password,
            script=(
                Rf'SCHTASKS /create /tn Agent /sc once /tr ""msiexec /passive /i ""C:\Users\jeanluc\Desktop\SentinelInstaller_windows_64bit.msi"" SITE_TOKEN={site_token}"" /ru interactive /rl highest /st 00:00 /f && SCHTASKS /run /tn Agent && SCHTASKS /delete /tn Agent /f'
            ),
        )

    if ip in ("192.168.192.22"):
        wait_until_online(vmx_path)
        logger.info(f"...Installing agent with site token '{site_token}'.")
        run_script(
            vmx_path=vmx_path,
            username=username,
            password=password,
            script=(
                Rf'SCHTASKS /create /tn Agent /sc once /tr ""msiexec /passive /i ""C:\Users\jeanluc\Desktop\SentinelInstaller_windows_32bit.msi"" SITE_TOKEN={site_token}"" /ru interactive /rl highest /st 00:00 /f && SCHTASKS /run /tn Agent && SCHTASKS /delete /tn Agent /f'
            ),
        )


def create_snapshot(vmx_path, name):
    subprocess.run(f'"{VMRUN_PATH}" -T ws snapshot "{vmx_path}" "{name}"', shell=True)
    logger.info(f"...Finished creating snapshot 'Baseline' for {vmx_path}.")
    sys.stdout.flush()


def restart(vmx_path):
    logger.info(f"...Issuing restart.")
    subprocess.run(
        f'"{VMRUN_PATH}" -T ws reset "{vmx_path}" soft',
        shell=True,
        capture_output=True,
    )


def wait_until_online(vmx_path):
    username = R"STARFLEET\jeanluc"
    password = R"Sentinelone!"
    logger.info(f"...Waiting for machine to be ready...")
    subprocess.run(
        rf'"{VMRUN_PATH}" -T ws -gu "{username}" -gp "{password}" runProgramInGuest "{vmx_path}" "C:\Windows\System32\whoami.exe"',
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
    #   logger.debug(f"...Running subprocess: {full_script}")
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
        logger.error(
            f"Failed to get the last 5 characters of the machine UUID. Error: {e}"
        )
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
    logger.info(f"...Creating directory {name}")
    os.makedirs(name, exist_ok=True)


def run_powershell(cmd):
    completed = subprocess.run(["powershell", "-Command", cmd], capture_output=True)
    return completed


def sigint_handler(sig, frame):
    logger.warning("User interrupted, exiting.")
    sys.exit(1)


def print_header():
    logger.debug("**********************")
    logger.debug("Python transcript start")
    logger.debug("Start time: " + datetime.datetime.today().strftime("%Y%m%d%H%M%S"))
    logger.debug("Python version: " + sys.version)
    logger.debug("**********************")


def print_footer():
    logger.debug("**********************")
    logger.debug("Python transcript end")
    logger.debug("End time: " + datetime.datetime.today().strftime("%Y%m%d%H%M%S"))
    logger.debug("**********************")


if __name__ == "__main__":
    main()
