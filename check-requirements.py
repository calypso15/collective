import math
import os
import platform
import psutil
import shutil

from enum import IntEnum
from subprocess import getoutput

class State(IntEnum):
    PASS = 0
    WARN = 1
    FAIL = 2
    FATAL = 4

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

def check_requirements() -> str:
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
        state = state | State.WARN
    print(f'  System reports processor name \'{test}\'')

    test = -(get_free_diskspace()//-(2**30))
    if test >= 500:
        print('Disk has at least 500GB of free space...PASS.')
    else:
        print('Disk has at least 500GB of free space...FAIL!')
        state = state | State.FAIL
    print(f'  System reports {test}GB of free space.')

    test = -(get_total_memory()//-(2**30))
    if test >= 64:
        print('System has at least 64GB of memory...PASS.')
    elif test >= 32:
        print('System has at least 64GB of memory...WARN.')
        state = state | State.WARN
    else:
        print('System has at least 64GB of memory...FAIL!')
        state = state | State.FAIL
    print(f'  System reports {test}GB of memory.')

    return State(2**math.floor(math.log2(state)))

print(check_requirements().name)