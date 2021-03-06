from __future__ import annotations

import multiprocessing as mp
import threading
from typing import Optional, Dict

import kombu
from pyrogram import idle

from tase.db.database_client import DatabaseClient
from tase.my_logger import logger
from tase.telegram import ClientTypes, TelegramClient
from tase.telegram.client_worker import ClientWorkerThread
from tase.telegram.handlers.base import ClientDisconnectHandler
from tase.telegram.handlers.bots import BotDeletedMessagesHandler, BotMessageHandler, CallbackQueryHandler, \
    ChosenInlineQueryHandler, InlineQueryHandler
from tase.telegram.handlers.users import UserChatMemberUpdatedHandler, UserDeletedMessagesHandler, UserMessageHandler


class ClientManager(mp.Process):
    def __init__(
            self,
            *,
            telegram_client_name: str,
            telegram_client: 'TelegramClient',
            task_queues: Dict['str', 'kombu.Queue'],
            database_client: 'DatabaseClient',
    ):
        super().__init__()
        self.name = telegram_client_name
        self.telegram_client: Optional['TelegramClient'] = telegram_client
        self.task_queues = task_queues
        self.db = database_client

    def run(self) -> None:
        logger.info(mp.current_process().name)
        logger.info(threading.current_thread())

        self.telegram_client.start()

        me = self.telegram_client.get_me()
        if me:
            self.telegram_client.telegram_id = me.id
            self.db.update_or_create_user(me)

        worker = ClientWorkerThread(
            telegram_client=self.telegram_client,
            index=0,
            db=self.db,
            task_queues=self.task_queues,
        )
        worker.start()

        self.init_handlers()
        self.register_update_handlers()

        idle()
        self.telegram_client.stop()

    def init_handlers(self):
        self.user_update_handlers = [
            UserChatMemberUpdatedHandler(
                db=self.db,
                task_queues=self.task_queues,
                telegram_client=self.telegram_client
            ),
            UserDeletedMessagesHandler(
                db=self.db,
                task_queues=self.task_queues,
                telegram_client=self.telegram_client
            ),
            UserMessageHandler(
                db=self.db,
                task_queues=self.task_queues,
                telegram_client=self.telegram_client
            ),
            # UserRawUpdateHandler(
            #     db=self.db,
            #     task_queues=self.task_queues,
            #     telegram_client=self.telegram_client
            # ),
        ]

        self.bot_update_handlers = [
            BotDeletedMessagesHandler(
                db=self.db,
                task_queues=self.task_queues,
                telegram_client=self.telegram_client
            ),
            BotMessageHandler(
                db=self.db,
                task_queues=self.task_queues,
                telegram_client=self.telegram_client
            ),
            # handlers.BotRawUpdateHandler(
            #     db=self.db,
            #     task_queues=self.task_queues,
            #     telegram_client=self.telegram_client
            # ),
            CallbackQueryHandler(
                db=self.db,
                task_queues=self.task_queues,
                telegram_client=self.telegram_client
            ),
            ChosenInlineQueryHandler(
                db=self.db,
                task_queues=self.task_queues,
                telegram_client=self.telegram_client
            ),
            InlineQueryHandler(
                db=self.db,
                task_queues=self.task_queues,
                telegram_client=self.telegram_client
            ),
        ]

        self.disconnect_handler = ClientDisconnectHandler(
            db=self.db,
            task_queues=self.task_queues,
            telegram_client=self.telegram_client
        )

    def register_update_handlers(self) -> None:
        """
        Register update handlers for this telegram client based on its type.
        """

        # register handler based on the type of the client
        if self.telegram_client.client_type == ClientTypes.USER:
            self.telegram_client.add_handlers(self.user_update_handlers)

        elif self.telegram_client.client_type == ClientTypes.BOT:
            self.telegram_client.add_handlers(self.bot_update_handlers)

            # todo: not working, why?
            # self.telegram_client.add_handler(
            #     ChatMemberUpdatedHandler(self.chat_member_update_handler.on_chat_member_updated)
            # )
        else:
            pass
        self.telegram_client.add_handlers([self.disconnect_handler])
