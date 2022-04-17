from typing import Optional

import tomli

from tase.my_logger import logger


def _get_config_from_file(file_path: str) -> Optional['dict']:
    try:
        with open(file_path, 'rb') as f:
            return tomli.load(f)
    except tomli.TOMLDecodeError as e:
        logger.exception(e)
    except Exception as e:
        logger.exception(e)

    return None
