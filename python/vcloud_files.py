import argparse
import hashlib
import json
import os
import requests
import sys
import tempfile
import traceback
import urllib


def download_file(filename):
    url = urllib.parse.urljoin(VCLOUD_URL, filename)
    datafile = os.path.join(DOWNLOAD_DIR, filename)

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
        for byte_block in iter(lambda: f.read(4096), b""):
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

    manifest_file = download_file('manifest.json')
    manifest = {}
    with open(os.path.join(DOWNLOAD_DIR, manifest_file)) as f:
        manifest = json.loads(f.read())

    print('Downloading OVAs...')

    for file in manifest['files']:
        try:
            name = file['name']
            hash_type = file['hash_type']
            hash_value = file['hash_value']

            print(f"Checking hash of '{name}'...", end='')
            sys.stdout.flush()

            if (not check_hash(name, hash_value, hash_type=hash_type)):
                print('does not match.')
                download_file(name)
            else:
                print('matches.')
        except Exception as e:
            print(e)

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
