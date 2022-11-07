import sys

from loguru import logger as _logger

logger_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "[{process.name}/{thread.name}] | "
    "<cyan>{module}</cyan>:<cyan>{function}()</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
)
log_config = {
    "handlers": [
        {"sink": sys.stderr, "format": logger_format},
    ],
}

_logger.configure(**log_config)
logger = _logger

if __name__ == "__main__":
    logger.debug("DEBUG")
    logger.info("INFO")
    logger.warning("WARNING")
    logger.error("ERROR")
    logger.critical("CRITICAL")
    logger.exception("EXCEPTION")
