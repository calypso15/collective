import hashlib
import os
import requests
import sys
import tempfile
import urllib

VCLOUD_URL = os.getenv('VCLOUD_URL')
VCLOUD_USER = os.getenv('VCLOUD_USER')
VCLOUD_PASS = os.getenv('VCLOUD_PASS')

AUTH = requests.auth.HTTPBasicAuth(VCLOUD_USER, VCLOUD_PASS)

TEMP_DIR = tempfile.gettempdir()
DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), 'Downloads', 'vcloud')

def download_file(filename):
    url = urllib.parse.urljoin(VCLOUD_URL, filename)
    datafile = os.path.join(DOWNLOAD_DIR, filename)

    local_filename = datafile

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


def check_hash(filename, hash):
    datafile = os.path.join(DOWNLOAD_DIR, filename)

    if (not os.path.isfile(datafile)):
        return False

    sha256_hash = hashlib.sha256()
    with open(datafile, 'rb') as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)

    return (sha256_hash.hexdigest() == hash)

if not os.path.exists(DOWNLOAD_DIR):
   os.makedirs(DOWNLOAD_DIR)

files = [
    'TheBorg-001.ova',
    'TheEnterpriseX64-002.ova',
    'TheMelbourneX64-003.ova',
    'TheSaratogaX86-004.ova'
]

for file in files:
    try:
        download_file(file+'.sha256')

        hash = None
        with open(os.path.join(DOWNLOAD_DIR, file+'.sha256'), 'r') as f:
            hash = f.read().rstrip()

        print(f"Checking hash of '{file}'...", end='')
        sys.stdout.flush()

        if (not check_hash(file, hash)):
            print('does not match.')
            download_file(file)
        else:
            print('matches.')
    except Exception as e:
        print(e)
