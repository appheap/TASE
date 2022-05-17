from enum import Enum
from typing import Optional

from .base_config import BaseConfig


class ClientTypes(Enum):
    UNKNOWN = "unknown"
    USER = "user"
    BOT = "bot"


class ClientConfig(BaseConfig):
    type: ClientTypes
    name: str
    role: str
    api_hash: str
    api_id: int
    bot_token: Optional[str]
