from enum import Enum


class ConnectionType(Enum):
    BASIC = "basic"
    JWT = "jwt"
    SUPERUSER_JWT = "superuser_jwt"
