import dotenv
import getpass
import hashlib
import json
import os
import requests
import sys
import tempfile
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


def download_files():
    global VCLOUD_URL, VCLOUD_USER, VCLOUD_PASS
    global AUTH
    global TEMP_DIR, DOWNLOAD_DIR

    with open('.env', 'a') as f:
        pass

    dotenv_file = dotenv.find_dotenv()
    dotenv.load_dotenv(dotenv_file)

    VCLOUD_URL = os.environ.get('VCLOUD_URL')
    VCLOUD_USER = os.environ.get('VCLOUD_USER')
    VCLOUD_PASS = os.environ.get('VCLOUD_PASS')

    new_url = False
    new_user = False
    new_pass = False

    first_pass = True
    max_retries = 3
    retries = 0

    while (first_pass or VCLOUD_URL == None or VCLOUD_USER == None or VCLOUD_PASS == None):
        first_pass = False

        if VCLOUD_URL == None:
            VCLOUD_URL = input('VM Cloud Url: ')
            new_url = True

        if VCLOUD_USER == None:
            VCLOUD_USER = input('VM Cloud User: ')
            new_user = True

        if VCLOUD_PASS == None:
            VCLOUD_PASS = getpass.getpass('VM Cloud Password: ')
            new_pass = True

        try:
            AUTH = requests.auth.HTTPBasicAuth(VCLOUD_USER, VCLOUD_PASS)
            r = requests.get(VCLOUD_URL, auth=AUTH)
            r.raise_for_status()
        except requests.exceptions.ConnectionError as e:
            print(e)
            VCLOUD_URL = None
        except requests.exceptions.HTTPError as e:
            print(e)
            code = e.response.status_code

            if code == 401:
                VCLOUD_USER = VCLOUD_PASS = None
        else:
            break

        if (retries < max_retries):
            print('There was a problem connecting to the server, trying again.')
            retries += 1
        else:
            print('Exceeded max retries, moving on.')
            break

    if new_url or new_user or new_pass:
        a = input('Save changes to VM Cloud environment variables [y/n]? ')

        if (a.lower() == 'y'):
            dotenv.set_key(dotenv_file, 'VCLOUD_URL', VCLOUD_URL)
            dotenv.set_key(dotenv_file, 'VCLOUD_USER', VCLOUD_USER)
            dotenv.set_key(dotenv_file, 'VCLOUD_PASS', VCLOUD_PASS)

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
    download_files()
