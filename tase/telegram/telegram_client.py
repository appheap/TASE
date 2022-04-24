from enum import Enum
from typing import Optional, Any, Coroutine, Union

import pyrogram
from pyrogram.handlers.handler import Handler

from tase.my_logger import logger
from .methods.search_messages import search_messages


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


class TelegramClient:
    _client: 'pyrogram.Client' = None
    name: 'str' = None
    api_id: 'int' = None
    api_hash: 'str' = None
    workdir: 'str' = None
    client_type: 'ClientTypes'

    def init_client(self):
        pass

    def start(self):
        if self._client is None:
            self.init_client()

        logger.info("#" * 50)
        logger.info(self.name)
        logger.info("#" * 50)
        self._client.start()

    def stop(self) -> Coroutine:
        return self._client.stop()

    def is_connected(self) -> bool:
        return self._client.is_connected

    def get_me(self) -> Coroutine[Any, Any, 'pyrogram.types.User']:
        return self._client.get_me()

    def get_chat(self, chat_id: Union[int, str]) -> Union["pyrogram.types.Chat", "pyrogram.types.ChatPreview"]:
        return self._client.get_chat(chat_id=chat_id)

    def get_session_name(self) -> str:
        return self._client.name

    def add_handler(self, handler: "Handler", group: int = 0):
        return self._client.add_handler(handler, group)

    def iter_audios(
            self,
            chat_id: Union['str', 'int'],
            query: str = "",
            offset: int = 0,
            offset_id: int = 0,
            only_newer_messages: bool = True,
    ):
        for message in search_messages(
                client=self._client,
                chat_id=chat_id,
                filter='audio',
                query=query,
                offset=offset,
                offset_id=offset_id,
                only_newer_messages=only_newer_messages,
        ):
            yield message

    @staticmethod
    def _parse(client_type: 'ClientTypes', client_configs: dict, workdir: str) -> Optional['TelegramClient']:
        if client_type == ClientTypes.USER:
            return UserTelegramClient(client_configs, workdir)
        elif client_type == ClientTypes.BOT:
            return BotTelegramClient(client_configs, workdir)
        else:
            # todo: raise error (unknown client type)
            logger.error("Unknown TelegramClient Type")
            pass


class UserTelegramClient(TelegramClient):
    role: 'UserClientRoles'

    def __init__(self, client_configs: dict, workdir: str):
        self.client_type = ClientTypes.USER
        self.workdir = workdir
        self.name = client_configs.get('name')
        self.api_id = client_configs.get('api_id')
        self.api_hash = client_configs.get('api_hash')
        self.role = UserClientRoles._parse(client_configs.get('role'))  # todo: check for unknown roles

    def init_client(self):
        self._client = pyrogram.Client(
            name=self.name,
            api_id=self.api_id,
            api_hash=self.api_hash,
            workdir=self.workdir,
        )


class BotTelegramClient(TelegramClient):
    role: 'BotClientRoles'
    token: 'str'

    def __init__(self, client_configs: dict, workdir: str):
        self.client_type = ClientTypes.BOT
        self.workdir = workdir
        self.name = client_configs.get('name')
        self.api_id = client_configs.get('api_id')
        self.api_hash = client_configs.get('api_hash')
        self.token = client_configs.get('bot_token')
        self.role = BotClientRoles._parse(client_configs.get('role'))  # todo: check for unknown roles

    def init_client(self):
        self._client = pyrogram.Client(
            name=self.name,
            api_id=self.api_id,
            api_hash=self.api_hash,
            bot_token=self.token,
            workdir=self.workdir,
        )
