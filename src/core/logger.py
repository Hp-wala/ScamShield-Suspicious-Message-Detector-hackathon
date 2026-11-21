import logging


logger = logging.getLogger("scamshield")
logger.setLevel(logging.INFO)
if not logger.handlers:
    logger.addHandler(logging.NullHandler())
