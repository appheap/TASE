from typing import List, Optional

from . import ArchiveChannelInfo
from .arangodb_config import ArangoDBConfig
from .base_config import BaseConfig
from .client_config import ClientConfig
from .elastic_config import ElasticConfig
from .pyrogram_config import PyrogramConfig


class TASEConfig(BaseConfig):
    arango_db_config: ArangoDBConfig
    elastic_config: ElasticConfig
    pyrogram_config: PyrogramConfig
    clients_config: List[ClientConfig]
    archive_channel_info: Optional[ArchiveChannelInfo]
