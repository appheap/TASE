import multiprocessing as mp
import threading
from typing import Optional, Dict

import kombu
from pyrogram import idle
from pyrogram.handlers import DisconnectHandler, MessageHandler, RawUpdateHandler, InlineQueryHandler, \
    DeletedMessagesHandler, ChosenInlineResultHandler, CallbackQueryHandler, ChatMemberUpdatedHandler

from tase.db.database_client import DatabaseClient
from tase.my_logger import logger
from tase.telegram import TelegramClient, ClientTypes
from tase.telegram import handlers
from tase.telegram.client_worker import ClientWorkerThread


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

        self.callback_query_handler = handlers.CallbackQueryHandler(
            db=self.db,
            task_queues=self.task_queues,
            telegram_client=self.telegram_client
        )

        self.chat_member_update_handler = handlers.ChatMemberUpdatedHandler(
            db=self.db,
            task_queues=self.task_queues,
            telegram_client=self.telegram_client
        )

        self.chosen_inline_query_handler = handlers.ChosenInlineQueryHandler(
            db=self.db,
            task_queues=self.task_queues,
            telegram_client=self.telegram_client
        )

        self.client_disconnect_handler = handlers.ClientDisconnectHandler(
            db=self.db,
            task_queues=self.task_queues,
            telegram_client=self.telegram_client
        )

        self.deleted_messages_handler = handlers.DeletedMessagesHandler(
            db=self.db,
            task_queues=self.task_queues,
            telegram_client=self.telegram_client
        )

        self.inline_query_handler = handlers.InlineQueryHandler(
            db=self.db,
            task_queues=self.task_queues,
            telegram_client=self.telegram_client
        )

        self.message_handler = handlers.MessageHandler(
            db=self.db,
            task_queues=self.task_queues,
            telegram_client=self.telegram_client
        )

        self.raw_update_handler = handlers.RawUpdateHandler(
            db=self.db,
            task_queues=self.task_queues,
            telegram_client=self.telegram_client
        )

    def run(self) -> None:
        logger.info(mp.current_process().name)
        logger.info(threading.current_thread())

        self.telegram_client.start()

        me = self.telegram_client.get_me()
        if me:
            self.telegram_client.telegram_id = me.id
            self.db.update_or_create_user(me)

        # register handler based on the type of the client
        if self.telegram_client.client_type == ClientTypes.USER:
            self.telegram_client.add_handler(MessageHandler(self.message_handler.on_message), group=0)
            self.telegram_client.add_handler(RawUpdateHandler(self.raw_update_handler.on_raw_update), group=1)
            self.telegram_client.add_handler(
                DeletedMessagesHandler(self.deleted_messages_handler.deleted_messages_handler),
                group=2
            )

            # todo: not working, why?
            self.telegram_client.add_handler(
                ChatMemberUpdatedHandler(self.chat_member_update_handler.on_chat_member_updated)
            )

        elif self.telegram_client.client_type == ClientTypes.BOT:
            self.telegram_client.add_handler(MessageHandler(self.message_handler.on_message))

            # todo: not working, why?
            self.telegram_client.add_handler(
                DeletedMessagesHandler(self.deleted_messages_handler.deleted_messages_handler)
            )

            self.telegram_client.add_handler(InlineQueryHandler(self.inline_query_handler.on_inline_query))
            self.telegram_client.add_handler(
                ChosenInlineResultHandler(self.chosen_inline_query_handler.on_chosen_inline_query)
            )
            self.telegram_client.add_handler(CallbackQueryHandler(self.callback_query_handler.on_callback_query))

            # todo: not working, why?
            self.telegram_client.add_handler(
                ChatMemberUpdatedHandler(self.chat_member_update_handler.on_chat_member_updated)
            )
        else:
            pass
        self.telegram_client.add_handler(DisconnectHandler(self.client_disconnect_handler.on_disconnect))

        worker = ClientWorkerThread(
            telegram_client=self.telegram_client,
            index=0,
            db=self.db,
            task_queues=self.task_queues,
        )
        worker.start()

        idle()
        self.telegram_client.stop()
