import math
import os
import platform
import psutil
import shutil
import sys

from enum import IntEnum
from subprocess import getoutput

class State(IntEnum):
    PASS = 1
    WARN = 2
    FAIL = 4
    FATAL = 8

def is_windows() -> bool:
    return platform.system() == 'Windows'

def is_admin() -> bool:
    try:
        temp = os.listdir(os.sep.join([os.environ.get('SystemRoot','C:\\windows'),'temp']))
    except:
        return False
    else:
        return True

def get_cpu_name() -> str:
    return getoutput('wmic cpu get name')

def get_free_diskspace() -> int:
    return shutil.disk_usage('.').free

def get_total_memory() -> int:
    return psutil.virtual_memory().total

def check() -> str:
    state = State.PASS

    if is_windows():
        print('System is running Windows...PASS.')
    else:
        print('System is running Windows...FATAL!')
        return State.FATAL

    if is_admin():
        print('Script is running as admin...PASS.')
    else:
        print('Script is running as admin...FAIL!')
        state = state | State.FAIL

    test = ''.join(get_cpu_name().split('\n')[1:]).strip()
    if 'i7' in test or 'i9' in test:
        print('System processor is Intel Core i7 or i9...PASS.')
    else:
        print('System processor is Intel Core i7 or i9...WARN.')
        print(f'  System reports processor name \'{test}\'')
        state = state | State.WARN

    test = -(get_free_diskspace()//-(2**30))
    if test >= 500:
        print('Disk has at least 500GB of free space...PASS.')
    else:
        print('Disk has at least 500GB of free space...FAIL!')
        print(f'  System reports {test}GB of free space.')
        state = state | State.FAIL

    test = -(get_total_memory()//-(2**30))
    if test >= 64:
        print('System has at least 64GB of memory...PASS.')
    elif test >= 32:
        print('System has at least 64GB of memory...WARN.')
        print(f'  System reports {test}GB of memory.')
        state = state | State.WARN
    else:
        print('System has at least 64GB of memory...FAIL!')
        print(f'  System reports {test}GB of memory.')
        state = state | State.FAIL


    return State(2**math.floor(math.log2(state)))

if __name__ == '__main__':
    print('Checking system requirements...')
    result = check()
    print('')

    if(result == State.PASS):
        print('This system meets all requirements.')
    elif(result == State.WARN):
        while(True):
            print('This system may be insufficient, proceed at your own risk. ', end='')
            answer = input('Proceed? [y/n] ')
            if answer.lower() in ["y","yes"]:
                break
            elif answer.lower() in ["n","no"]:
                print('Aborting.')
                sys.exit(1)

    else:
        print('This system does not meet the minimum requirements, aborting.')
        sys.exit(1)