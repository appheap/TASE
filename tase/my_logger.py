from logging import CRITICAL, DEBUG, ERROR, FATAL, INFO, Logger, NOTSET, WARNING

import colorlog
from decouple import config

_nameToLevel = {
    "CRITICAL": CRITICAL,
    "FATAL": FATAL,
    "ERROR": ERROR,
    "WARN": WARNING,
    "WARNING": WARNING,
    "INFO": INFO,
    "DEBUG": DEBUG,
    "NOTSET": NOTSET,
}


def init_logger() -> "Logger":
    handler = colorlog.StreamHandler()
    handler.setFormatter(
        colorlog.ColoredFormatter(
            "[%(log_color)s%(asctime)s: %(levelname)s/%(processName)s:%(threadName)s] %(message)s"
        )
    )
    logger = colorlog.getLogger(__name__)
    logger.propagate = False
    logger.addHandler(handler)
    logger.setLevel(_nameToLevel[config("LOGGING_LEVEL")])

    return logger


logger = init_logger()

if __name__ == "__main__":
    logger.debug("DEBUG")
    logger.info("INFO")
    logger.warning("WARNING")
    logger.error("ERROR")
    logger.critical("CRITICAL")
    logger.exception("EXCEPTION")
