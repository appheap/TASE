from .base_config import BaseConfig


class ElasticConfig(BaseConfig):
    cluster_url: str
    https_certs_url: str
    basic_auth_username: str
    basic_auth_password: str
