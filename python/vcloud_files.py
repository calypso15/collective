import argparse
import ctypes
import hashlib
import json
import os
import requests
import sys
import tempfile
import traceback
import urllib


def download_file(filename, path = None):
    if path == None:
        path = DOWNLOAD_DIR

    url = urllib.parse.urljoin(VCLOUD_URL, filename)
    datafile = os.path.join(path, filename)

    local_filename = urllib.parse.unquote(datafile)

    with requests.get(url, auth=AUTH, stream=True) as r:
        r.raise_for_status()
        chunk_size = 1024*1024
        total_size = int(r.headers.get('content-length', 0))

        with open(local_filename, 'wb') as f:
            current_size = 0

            for chunk in r.iter_content(chunk_size=chunk_size):
                current_size += len(chunk)
                progress = round(100*current_size/total_size, 2)
                print(
                    f'\rDownloading {url}... {current_size//(1024*1024)} MB / {total_size//(1024*1024)} MB, {progress}%', end='')
                f.write(chunk)

            print('')

    return local_filename


def check_hash(filename, hash_value, hash_type='sha256'):
    datafile = os.path.join(DOWNLOAD_DIR, filename)

    if (not os.path.isfile(datafile)):
        return False

    alg = hashlib.new(hash_type)
    with open(datafile, 'rb') as f:
        for byte_block in iter(lambda: f.read(65536), b""):
            alg.update(byte_block)

    return (alg.hexdigest() == hash_value)


def download_files(vcloud_url, vcloud_user, vcloud_pass):
    global AUTH
    global TEMP_DIR, DOWNLOAD_DIR
    global VCLOUD_URL, VCLOUD_USER, VCLOUD_PASS

    VCLOUD_URL = vcloud_url
    VCLOUD_USER = vcloud_user
    VCLOUD_PASS = vcloud_pass

    try:
        AUTH = requests.auth.HTTPBasicAuth(vcloud_user, vcloud_pass)
        r = requests.get(vcloud_url, auth=AUTH)
        r.raise_for_status()
    except requests.ConnectionError as x:
        print(traceback.format_exc())
        print(f"Unable to connect to {vcloud_url}, exiting. Please contact ryan.ogrady@sentinelone.com for additional support.")
        sys.exit()
    except requests.HTTPError as x:
        print(traceback.format_exc())
        print(f"Received HTTP {x.response.status_code}, exiting. Please contact ryan.ogrady@sentinelone.com for additional support.")
        sys.exit()

    TEMP_DIR = tempfile.gettempdir()
    DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), 'Documents', '.vcloud')

    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    if os.path.exists(os.path.join(DOWNLOAD_DIR, 'manifest.json')):
        old_manifest = {}
        with open(os.path.join(DOWNLOAD_DIR, 'manifest.json')) as f:
            old_manifest = json.loads(f.read())

        new_manifest = {}
        with tempfile.TemporaryDirectory() as tmpdirname:
            download_file('manifest.json', tmpdirname)
            with open(os.path.join(tmpdirname, 'manifest.json')) as f:
                new_manifest = json.loads(f.read())

        if new_manifest['version'] > old_manifest['version']:
            rv = ctypes.windll.user32.MessageBoxW(0, f"There is a newer version (v{new_manifest['version']}) of the virtual environment. Do you want to download it?", "Download virtual environment?", 0x4 ^ 0x40 ^ 0x1000)

            if (rv != 6):
                print('Skipping environment download.')
                return
        else:
            return

    manifest = new_manifest

    print('Downloading OVAs...')

    sorted_list = sorted(manifest['files'], key=lambda d: d.get('order', sys.maxsize))
    for file in sorted_list:
        try:
            name = file['name']
            hash_type = file['hash_type']
            hash_value = file['hash_value']

            print(f"Checking hash of '{name}'...", end='')
            sys.stdout.flush()

            if (not os.path.isfile(os.path.join(DOWNLOAD_DIR, name))):
                print('file missing.')
                download_file(name)
            elif (not check_hash(name, hash_value, hash_type=hash_type)):
                print('does not match.')
                download_file(name)
            else:
                print('matches.')
        except Exception as e:
            print(e)

    with open(os.path.join(DOWNLOAD_DIR, 'manifest.json'), 'w') as f:
        f.write(json.dumps(manifest, indent=4))

    print('Finished downloading OVAs.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file')
    args = parser.parse_args()

    config = {}
    config_file = args.config_file
    with open(config_file) as f:
        config = json.loads(f.read())

    download_files(config['Vcloud']['Url'], config['Vcloud']['Username'], config['Vcloud']['Password'])
