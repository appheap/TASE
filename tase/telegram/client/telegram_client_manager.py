import asyncio
import multiprocessing as mp
import sys
import threading
from typing import List, Optional

import uvloop
from pyrogram import idle

from tase.configs import TASEConfig, ClientTypes
from tase.db import DatabaseClient
from tase.my_logger import logger
from tase.telegram.client import TelegramClient, UserTelegramClient
from tase.telegram.client.client_worker import TelegramClientConsumer
from tase.telegram.update_handlers.base import ClientDisconnectHandler
from tase.telegram.update_handlers.bots import BotDeletedMessagesHandler, BotMessageHandler, CallbackQueryHandler, ChosenInlineQueryHandler, InlineQueryHandler
from tase.telegram.update_handlers.users import UserChatMemberUpdatedHandler, UserDeletedMessagesHandler, UserMessageHandler


class TelegramClientManager(mp.Process):
    def __init__(
        self,
        config: TASEConfig,
    ):
        super(TelegramClientManager, self).__init__()

        self.name = "TelegramClientManager"
        self.config: TASEConfig = config
        self.db: Optional[DatabaseClient] = None
        self.rabbitmq_consumer: Optional[TelegramClientConsumer] = None

        self.clients: List[TelegramClient] = []
        self.users: List[TelegramClient] = []
        self.bots: List[TelegramClient] = []

    def run(self) -> None:
        logger.info(f"process: {mp.current_process().name}, thread: {threading.current_thread()}")

        if sys.version_info >= (3, 11):
            with asyncio.Runner(loop_factory=uvloop.new_event_loop) as runner:
                runner.run(self.run_telegram_client_manager())
        else:
            uvloop.install()
            asyncio.run(self.run_telegram_client_manager())

    async def run_telegram_client_manager(self):
        # initialize database client for this process
        self.db = DatabaseClient(
            self.config.elastic_config,
            self.config.arango_db_config,
        )
        await self.db.init_databases()

        self.rabbitmq_consumer = TelegramClientConsumer(db=self.db)

        for client_config in self.config.clients_config:
            telegram_client = TelegramClient.parse(
                client_config,
                self.config.pyrogram_config.workdir,
            )
            # set the archive channel info for the client
            telegram_client.archive_channel_info = self.config.archive_channel_info
            telegram_client.thumbnail_archive_channel_info = self.config.thumbnail_archive_channel_info

            await telegram_client.start()

            self.clients.append(telegram_client)
            if isinstance(telegram_client, UserTelegramClient):
                self.users.append(telegram_client)
            else:
                self.bots.append(telegram_client)

            await telegram_client.set_bot_commands(self.db.graph.get_bot_commands_list_for_telegram(await self.db.graph.get_admins_and_owners()))

            me = await telegram_client.get_me()
            if me:
                telegram_client.telegram_id = me.id
                await self.db.graph.get_interacted_user(me, update=True)

            # check if the client has cached the archive channel
            if not await telegram_client.peer_exists(telegram_client.archive_channel_info.chat_id):
                archived_chat = await telegram_client.get_chat(telegram_client.archive_channel_info.chat_id)
                if archived_chat:
                    # update or create the archived chat in the database
                    await self.db.graph.update_or_create_chat(archived_chat)

            self.init_handlers(telegram_client)
            self.register_update_handlers(telegram_client)

        await self.rabbitmq_consumer.init_rabbitmq_consumer(self.users, self.bots)

        await idle()
        for client in self.clients:
            await client.stop()

        await self.rabbitmq_consumer.shutdown()

    def init_handlers(
        self,
        telegram_client: TelegramClient,
    ):
        self.user_update_handlers = [
            UserChatMemberUpdatedHandler(
                db=self.db,
                telegram_client=telegram_client,
            ),
            UserDeletedMessagesHandler(
                db=self.db,
                telegram_client=telegram_client,
            ),
            UserMessageHandler(
                db=self.db,
                telegram_client=telegram_client,
            ),
            # UserRawUpdateHandler(
            #     db=self.db,
            #     telegram_client=telegram_client
            # ),
        ]

        self.bot_update_handlers = [
            BotDeletedMessagesHandler(
                db=self.db,
                telegram_client=telegram_client,
            ),
            BotMessageHandler(
                db=self.db,
                telegram_client=telegram_client,
            ),
            # BotRawUpdateHandler(
            #     db=self.db,
            #     telegram_client=telegram_client
            # ),
            CallbackQueryHandler(
                db=self.db,
                telegram_client=telegram_client,
            ),
            ChosenInlineQueryHandler(
                db=self.db,
                telegram_client=telegram_client,
            ),
            InlineQueryHandler(
                db=self.db,
                telegram_client=telegram_client,
            ),
        ]

        self.disconnect_handler = ClientDisconnectHandler(
            db=self.db,
            telegram_client=telegram_client,
        )

    def register_update_handlers(
        self,
        telegram_client: TelegramClient,
    ) -> None:
        """
        Register update handlers for this telegram client based on its type.
        """

        # register handler based on the type of the client
        if telegram_client.client_type == ClientTypes.USER:
            telegram_client.add_handlers(self.user_update_handlers)

        elif telegram_client.client_type == ClientTypes.BOT:
            telegram_client.add_handlers(self.bot_update_handlers)

            # todo: not working, why?
            # telegram_client.add_handler(
            #     ChatMemberUpdatedHandler(self.chat_member_update_handler.on_chat_member_updated)
            # )
        else:
            pass
        telegram_client.add_handlers([self.disconnect_handler])
