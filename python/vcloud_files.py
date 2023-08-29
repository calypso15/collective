import argparse
import ctypes
import hashlib
import json
import os
import requests
import sys
import tempfile
import timeit
import traceback
import urllib


def download_file(url, filename, local_dir=None, auth=None):
    if local_dir == None:
        local_dir = DOWNLOAD_DIR

    url = urllib.parse.urljoin(url, filename)
    datafile = os.path.join(local_dir, filename)

    local_filename = urllib.parse.unquote(datafile)

    with requests.get(url, auth=auth, stream=True) as r:
        r.raise_for_status()
        chunk_size = 1024 * 1024
        total_size = int(r.headers.get("content-length", 0))

        with open(local_filename, "wb") as f:
            current_size = 0

            for chunk in r.iter_content(chunk_size=chunk_size):
                current_size += len(chunk)
                progress = round(100 * current_size / total_size, 2)
                print(
                    f"\rDownloading {url}... {current_size//(1024*1024)} MB / {total_size//(1024*1024)} MB, {progress}%",
                    end="",
                )
                f.write(chunk)

            print("")

    return local_filename


def check_hash(filename, hash_value, hash_type="sha256"):
    datafile = os.path.join(DOWNLOAD_DIR, filename)

    if not os.path.isfile(datafile):
        return False

    alg = hashlib.new(hash_type)
    with open(datafile, "rb") as f:
        for byte_block in iter(lambda: f.read(2**16), b""):
            alg.update(byte_block)

    return alg.hexdigest() == hash_value


def download_files(url, auth):
    global TEMP_DIR, DOWNLOAD_DIR

    TEMP_DIR = tempfile.gettempdir()
    DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Documents", ".vcloud")

    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    manifest = None
    with tempfile.TemporaryDirectory() as tmpdirname:
        download_file(
            url=url, filename="manifest.json", local_dir=tmpdirname, auth=auth
        )
        with open(os.path.join(tmpdirname, "manifest.json")) as f:
            manifest = json.loads(f.read())

    if os.path.exists(os.path.join(DOWNLOAD_DIR, "manifest.json")):
        old_manifest = None
        with open(os.path.join(DOWNLOAD_DIR, "manifest.json")) as f:
            old_manifest = json.loads(f.read())

        if manifest["version"] > old_manifest["version"]:
            rv = ctypes.windll.user32.MessageBoxW(
                0,
                f"There is a newer version (v{manifest['version']}) of the virtual environment. Do you want to download it?",
                "Download virtual environment?",
                0x4 ^ 0x40 ^ 0x1000,
            )

            if rv != 6:
                print("Skipping environment download at user request.")
                manifest = None
        else:
            print("Skipping environment download, environment is up-to-date.")
            manifest = None

    if manifest != None:
        print("Downloading OVAs...")
        sorted_list = sorted(
            manifest["files"], key=lambda d: d.get("order", sys.maxsize)
        )
        for file in sorted_list:
            try:
                name = file["name"]
                hash_type = file["hash_type"]
                hash_value = file["hash_value"]

                print(f"Checking hash of '{name}'...", end="")
                sys.stdout.flush()

                if not os.path.isfile(os.path.join(DOWNLOAD_DIR, name)):
                    print("file missing.")
                    download_file(name)
                elif not check_hash(name, hash_value, hash_type=hash_type):
                    print("does not match.")
                    download_file(name)
                else:
                    print("matches.")
            except Exception as e:
                print(e)

        with open(os.path.join(DOWNLOAD_DIR, "manifest.json"), "w") as f:
            f.write(json.dumps(manifest, indent=4))

        print("Finished downloading OVAs.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("config_file")
    args = parser.parse_args()

    config = {}
    config_file = args.config_file
    with open(config_file) as f:
        config = json.loads(f.read())

    download_files(
        config["Vcloud"]["Url"],
        config["Vcloud"]["Username"],
        config["Vcloud"]["Password"],
    )
