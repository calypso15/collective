import argparse
import json
import logging
import math
import os
import platform
import psutil
import shutil
import sys

from enum import IntEnum
from subprocess import getoutput

import log_config

logger = logging.getLogger(__name__)


class State(IntEnum):
    PASS = 1
    WARN = 2
    FAIL = 4
    FATAL = 8


def is_windows() -> bool:
    return platform.system() == "Windows"


def is_admin() -> bool:
    try:
        temp = os.listdir(
            os.sep.join([os.environ.get("SystemRoot", "C:\\windows"), "temp"])
        )
    except:
        return False
    else:
        return True


def get_cpu_name() -> str:
    return getoutput("wmic cpu get name")


def get_free_diskspace() -> int:
    return shutil.disk_usage(".").free


def get_total_memory() -> int:
    return psutil.virtual_memory().total


def check() -> str:
    state = State.PASS

    if is_windows():
        logger.info("System is running Windows...PASS.")
    else:
        logger.error("System is running Windows...FATAL!")
        return State.FATAL

    if is_admin():
        logger.info("Script is running as admin...PASS.")
    else:
        logger.error("Script is running as admin...FAIL!")
        state = state | State.FAIL

    test = "".join(get_cpu_name().split("\n")[1:]).strip()
    if "i7" in test or "i9" in test:
        logger.info("System processor is Intel Core i7 or i9...PASS.")
    else:
        logger.warning("System processor is Intel Core i7 or i9...WARN.")
        logger.warning(f"  System reports processor name '{test}'")
        state = state | State.WARN

    test = -(get_free_diskspace() // -(2**30))
    if test >= 250:
        logger.info("Disk has at least 250GB of free space...PASS.")
    elif test >= 150:
        logger.warning("Disk has at least 250GB of free space...WARN!")
        logger.warning(f"  System reports {test}GB of free space.")
        state = state | State.WARN
    else:
        logger.error("Disk has at least 250GB of free space...FAIL!")
        logger.error(f"  System reports {test}GB of free space.")
        state = state | State.FAIL

    test = -(get_total_memory() // -(2**30))
    if test >= 64:
        logger.info("System has at least 64GB of memory...PASS.")
    elif test >= 32:
        logger.warning("System has at least 64GB of memory...WARN.")
        logger.warning(f"  System reports {test}GB of memory.")
        state = state | State.WARN
    else:
        logger.error("System has at least 64GB of memory...FAIL!")
        logger.error(f"  System reports {test}GB of memory.")
        state = state | State.FAIL

    return State(2 ** math.floor(math.log2(state)))


def check_requirements(ignore_warnings=False, ignore_errors=False):
    logger.info("Checking system requirements...")
    result = check()

    if result == State.PASS:
        logger.info("This system meets all requirements.")
    elif result == State.WARN:
        if ignore_warnings:
            logger.warning(
                "This system may be insufficient, but IgnoreWarnings is set to true."
            )
        else:
            logger.error(
                "This system may be insufficient. To proceed anyway, change '\"IgnoreWarnings\": false' in the config file to '\"IgnoreWarnings\": true' and re-run setup."
            )
            sys.exit(1)
    elif result == State.FAIL:
        if ignore_errors:
            logger.warning(
                "This system does not meet the minimum requirements, but IgnoreErrors is set to true."
            )
        else:
            logger.error(
                "This system does not meet the minimum requirements, aborting. To proceed anyway, change '\"IgnoreErrors\": false' in the config file to '\"IgnoreErrors\": true' and re-run setup."
            )
            sys.exit(1)
    else:
        logger.error("This system does not meet the minimum requirements, aborting.")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("config_file")
    args = parser.parse_args()

    config = {}
    config_file = args.config_file
    with open(config_file) as f:
        config = json.loads(f.read())

    check_requirements(
        ignore_warnings=config.get("IgnoreWarnings", False),
        ignore_errors=config.get("IgnoreErrors", False),
    )
