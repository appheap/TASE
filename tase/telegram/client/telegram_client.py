from __future__ import annotations

import re
from datetime import datetime
from enum import Enum
from typing import Coroutine, Iterable, List, Optional, Union, Dict, Any, AsyncGenerator, TYPE_CHECKING

import pyrogram
from pyrogram.errors import PeerIdInvalid, ChannelInvalid
from pyrogram.handlers.handler import Handler

from tase.configs import ClientConfig, ClientTypes, ArchiveChannelInfo
from tase.my_logger import logger
from tase.telegram.client.raw_methods import search_messages, forward_messages

if TYPE_CHECKING:
    from tase.telegram.update_handlers.base import BaseHandler


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


class TelegramClient:
    _client: pyrogram.Client = None
    name: str = None
    api_id: int = None
    api_hash: str = None
    workdir: str = None
    telegram_id: int = None
    client_type: ClientTypes
    _me: Optional[pyrogram.types.User] = None

    archive_channel_info: Optional[ArchiveChannelInfo]

    def init_client(self):
        pass

    async def start(self):
        if self._client is None:
            self.init_client()

        logger.info("#" * 50)
        logger.info(self.name)
        logger.info("#" * 50)
        await self._client.start()

    async def set_bot_commands(
        self,
        commands_list: List[Dict[str, Any]],
    ):
        pass

    async def stop(self) -> Coroutine:
        return await self._client.stop()

    def is_connected(self) -> bool:
        return self._client.is_connected

    async def peer_exists(
        self,
        peer_id: Union[str, int],
    ) -> bool:
        """
        Check whether a peer exists in the local DB or not

        Parameters
        ----------
        peer_id : str or int
            Peer ID to check. Can be username, chat ID, user ID, phone number, etc.

        Returns
        -------
        bool
            Whether the peer exists in the DB or not

        """
        try:
            # peer = self._client.resolve_peer(peer_id)
            peer = await self._client.storage.get_peer_by_id(peer_id)
        except KeyError:
            # peer does not exist

            if isinstance(peer_id, str):
                if peer_id in ("self", "me"):
                    return True

                peer_id = re.sub(r"[@+\s]", "", peer_id.lower())

                try:
                    int(peer_id)
                except ValueError:
                    try:
                        peer = await self._client.storage.get_peer_by_username(peer_id)
                    except KeyError:
                        pass
                    else:
                        if peer:
                            return True
                else:
                    try:
                        peer = await self._client.storage.get_peer_by_phone_number(peer_id)
                    except KeyError:
                        return False
                    else:
                        if peer:
                            return True

        except ValueError:
            # invalid peer type
            pass
        except Exception as e:
            logger.exception(e)
        else:
            if peer:
                return True

        return False

    async def get_me(self) -> Optional[pyrogram.types.User]:
        # todo: add a feature to update this on fixed intervals to have latest information
        if self._me is None:
            self._me = await self._client.get_me()
        return self._me

    async def get_chat(
        self,
        chat_id: Union[int, str],
    ) -> Union[pyrogram.types.Chat, pyrogram.types.ChatPreview]:
        return await self._client.get_chat(chat_id=chat_id)

    async def forward_messages(
        self,
        chat_id: Union[int, str],
        from_chat_id: Union[int, str],
        message_ids: Union[int, Iterable[int]],
        disable_notification: bool = None,
        schedule_date: datetime = None,
        protect_content: bool = None,
        drop_media_captions: Optional[bool] = False,
        drop_author: Optional[bool] = False,
    ) -> Union[pyrogram.types.Message, List[pyrogram.types.Message]]:
        return await forward_messages(
            self._client,
            chat_id=chat_id,
            from_chat_id=from_chat_id,
            message_ids=message_ids,
            disable_notification=disable_notification,
            schedule_date=schedule_date,
            protect_content=protect_content,
            drop_author=drop_author,
            drop_media_captions=drop_media_captions,
        )

    def get_session_name(self) -> str:
        return self._client.name

    def add_handler(
        self,
        handler: pyrogram.handlers.handler.Handler,
        group: int = 0,
    ):
        return self._client.add_handler(handler, group)

    def add_handlers(
        self,
        handlers_list: List[BaseHandler],
    ):
        for handler in handlers_list:
            for h in handler.init_handlers():
                self.add_handler(
                    h.cls(
                        callback=h.callback,
                        filters=h.filters,
                    )
                    if h.has_filter
                    else h.cls(
                        callback=h.callback,
                    ),
                    h.group,
                )

    def iter_messages(
        self,
        chat_id: Union[str, int],
        query: str = "",
        offset: int = 0,
        offset_id: int = 0,
        only_newer_messages: bool = True,
        filter: str = "empty",
    ) -> Optional[AsyncGenerator[pyrogram.types.Message, None]]:
        return search_messages(
            client=self._client,
            chat_id=chat_id,
            query=query,
            offset=offset,
            offset_id=offset_id,
            only_newer_messages=only_newer_messages,
            filter=filter,
        )

    @classmethod
    def parse(
        cls,
        client_config: ClientConfig,
        workdir: str,
    ) -> Optional[TelegramClient]:
        if client_config.type == ClientTypes.USER:
            return UserTelegramClient(
                client_config,
                workdir,
            )
        elif client_config.type == ClientTypes.BOT:
            return BotTelegramClient(
                client_config,
                workdir,
            )
        else:
            # todo: raise error (unknown client type)
            logger.error("Unknown TelegramClient Type")

    async def get_messages(
        self,
        chat_id: Union[int, str],
        message_ids: Union[int, Iterable[int]] = None,
    ) -> Union[pyrogram.types.Message, List[pyrogram.types.Message]]:
        if chat_id is None or not message_ids:
            return []

        try:
            messages = await self._client.get_messages(
                chat_id=chat_id,
                message_ids=message_ids,
            )
            if messages and not isinstance(messages, list):
                messages = [messages]
        except KeyError as e:
            # chat is no longer has that username or the username is invalid
            logger.error(f"[KeyError] Chat ID `{chat_id}` no longer has this username or the username is invalid!")
            raise e
        except ChannelInvalid as e:
            # The channel parameter is invalid
            logger.error(f"[ChannelInvalid] Chat ID `{chat_id}` is no longer valid!")
            raise e
        except Exception as e:
            # fixme
            logger.exception(e)
            raise e

        return messages


class UserTelegramClient(TelegramClient):
    role: UserClientRoles

    def __init__(
        self,
        client_config: ClientConfig,
        workdir: str,
    ):
        self.client_type = ClientTypes.USER
        self.workdir = workdir
        self.name = client_config.name
        self.api_id = client_config.api_id
        self.api_hash = client_config.api_hash
        self.role = UserClientRoles._parse(client_config.role)  # todo: check for unknown roles

    def init_client(self):
        self._client = pyrogram.Client(
            name=self.name,
            api_id=self.api_id,
            api_hash=self.api_hash,
            workdir=self.workdir,
            # proxy={
            #     "scheme": "socks5",
            #     "hostname": "127.0.0.1",
            #     "port": 9150,
            #     "username": None,
            #     "password": None,
            # },
        )


class BotTelegramClient(TelegramClient):
    role: BotClientRoles
    token: str

    def __init__(
        self,
        client_config: ClientConfig,
        workdir: str,
    ):
        self.client_type = ClientTypes.BOT
        self.workdir = workdir
        self.name = client_config.name
        self.api_id = client_config.api_id
        self.api_hash = client_config.api_hash
        self.token = client_config.bot_token
        self.role = BotClientRoles._parse(client_config.role)  # todo: check for unknown roles

    def init_client(self):
        self._client = pyrogram.Client(
            name=self.name,
            api_id=self.api_id,
            api_hash=self.api_hash,
            bot_token=self.token,
            workdir=self.workdir,
            # proxy={
            #     "scheme": "socks5",
            #     "hostname": "127.0.0.1",
            #     "port": 9150,
            #     "username": None,
            #     "password": None,
            # },
        )

    async def set_bot_commands(
        self,
        commands_list: List[Dict[str, Any]],
    ):
        for command_arg in commands_list:
            try:
                await self._client.set_bot_commands(
                    command_arg["commands"],
                    command_arg["scope"],
                )
            except PeerIdInvalid as e:
                # todo: the user is not queried the bot yet, so it needs to be cached

                logger.error("peer invalid")
            except Exception as e:
                logger.exception(e)
