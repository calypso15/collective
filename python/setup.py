import sys

import vcloud_files
import system_requirements

if __name__ == '__main__':
    system_requirements.check_requirements()
    vcloud_files.download_files()
