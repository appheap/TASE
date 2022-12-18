from enum import Enum

from .base_config import BaseConfig


class ArchiveChannelType(Enum):
    TEST = "test"
    PRODUCTION = "production"


class ArchiveChannelInfo(BaseConfig):
    chat_id: int
    type: ArchiveChannelType
