import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

ROOT_PATH = Path(__file__).resolve().parents[2]
LOG_DIR = ROOT_PATH / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / 'spam_detector.log'

logger = logging.getLogger('spam_detector')
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s')

file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def safe_log(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            try:
                logger.exception('Logging failure')
            except Exception:
                pass
    return wrapper
