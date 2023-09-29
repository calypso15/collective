import logging
import os

HOME = os.path.expanduser("~")
DOCUMENTS_DIR = os.path.join(HOME, "Documents")
LOG_FILENAME = os.path.join(DOCUMENTS_DIR, "log-python.txt")

console_format = logging.Formatter("%(levelname)s: %(message)s")
file_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(console_format)

file_handler = logging.FileHandler(LOG_FILENAME, "a", "utf-8")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(file_format)

logging.getLogger().addHandler(console_handler)
logging.getLogger().addHandler(file_handler)
logging.getLogger().setLevel(logging.DEBUG)
