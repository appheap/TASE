from .base_config import BaseConfig


class ArangoDBConfig(BaseConfig):
    db_host_url: str
    db_name: str
    db_username: str
    db_password: str
    graph_name: str
