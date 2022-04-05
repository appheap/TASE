from enum import Enum
from typing import Optional

import pyrogram


class UserClientRoles(Enum):
    UNKNOWN = 0
    INDEXER = 1

    @staticmethod
    def _parse(role: str):
        for item in UserClientRoles:
            if item.name == role:
                return item
        else:
            return UserClientRoles.UNKNOWN


class BotClientRoles(Enum):
    UNKNOWN = 0
    MAIN = 1

    @staticmethod
    def _parse(role: str):
        for item in BotClientRoles:
            if item.name == role:
                return item
        else:
            return BotClientRoles.UNKNOWN


class ClientTypes(Enum):
    UNKNOWN = 0
    USER = 1
    BOT = 2


class Client:
    _client: 'pyrogram.Client' = None
    name: 'str' = None
    api_id: 'int' = None
    api_hash: 'str' = None
    workdir: 'str' = None

    def init_client(self):
        pass

    def connect(self):
        if self._client is None:
            self.init_client()

        print("#" * 50)
        print(self.name)
        print("#" * 50)
        self._client.start()

    def is_connected(self) -> bool:
        return self._client.is_connected

    def get_me(self):
        return self._client.get_me()

    @staticmethod
    def _parse(client_type: 'ClientTypes', client_configs: dict, workdir: str) -> Optional['Client']:
        if client_type == ClientTypes.USER:
            return UserClient(client_configs, workdir)
        elif client_type == ClientTypes.BOT:
            return BotClient(client_configs, workdir)
        else:
            # todo: raise error (unknown client type)
            pass


class UserClient(Client):
    role: 'UserClientRoles'

    def __init__(self, client_configs: dict, workdir: str):
        self.workdir = workdir
        self.name = client_configs.get('name')
        self.api_id = client_configs.get('api_id')
        self.api_hash = client_configs.get('api_hash')
        self.role = UserClientRoles._parse(client_configs.get('role'))  # todo: check for unknown roles

    def init_client(self):
        self._client = pyrogram.Client(
            session_name=self.name,
            api_id=self.api_id,
            api_hash=self.api_hash,
            workdir=self.workdir,
        )


class BotClient(Client):
    role: 'BotClientRoles'
    token: 'str'

    def __init__(self, client_configs: dict, workdir: str):
        self.workdir = workdir
        self.name = client_configs.get('name')
        self.api_id = client_configs.get('api_id')
        self.api_hash = client_configs.get('api_hash')
        self.token = client_configs.get('bot_token')
        self.role = BotClientRoles._parse(client_configs.get('role'))  # todo: check for unknown roles

    def init_client(self):
        self._client = pyrogram.Client(
            session_name=self.name,
            api_id=self.api_id,
            api_hash=self.api_hash,
            bot_token=self.token,
            workdir=self.workdir,
        )
