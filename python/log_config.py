import logging
import os

HOME = os.path.expanduser("~")
DOCUMENTS_DIR = os.path.join(HOME, "Documents")
LOG_FILENAME = os.path.join(DOCUMENTS_DIR, "log-python.txt")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILENAME, "a", "utf-8"), logging.StreamHandler()],
)
