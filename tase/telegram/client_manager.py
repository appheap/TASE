import multiprocessing as mp
import threading
from typing import Optional, List, Union, Dict

import arrow as arrow
import kombu
import pyrogram
from pyrogram import raw
from pyrogram import types, idle
from pyrogram.handlers import DisconnectHandler, MessageHandler, RawUpdateHandler, InlineQueryHandler, \
    DeletedMessagesHandler, ChosenInlineResultHandler, CallbackQueryHandler, ChatMemberUpdatedHandler

from tase.db.database_client import DatabaseClient
from tase.my_logger import logger
from tase.telegram import TelegramClient, ClientTypes
from tase.telegram.client_worker import ClientWorkerThread
from tase.telegram.globals import client_task
from tase.telegram.tasks.index_audios_task import IndexAudiosTask


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

    def on_message(
            self,
            client: 'pyrogram.Client',
            message: 'types.Message'
    ):
        if self.telegram_client.client_type == ClientTypes.USER:
            # the client type is a user
            # logger.info(message)
            logger.info(f'on_message : {message.chat.title}')
            pass
        elif self.telegram_client.client_type == ClientTypes.BOT:
            # the client type is a bot
            logger.info(message)
        else:
            # the client type is unknown, raise an error
            pass

    def on_raw_update(
            self,
            client: 'pyrogram.Client',
            raw_update: '_update',
            users: List['types.User'],
            chats: List['types.Chat']
    ):
        # logger.info(f"on_raw_update: {raw_update}")
        pass

    def on_chat_member_updated(self, client: 'pyrogram.Client', chat_member_updated: 'types.ChatMemberUpdated'):
        logger.info(f"on_chat_member_updated: {chat_member_updated}")

    def on_inline_query(self, client: 'pyrogram.Client', inline_query: 'types.InlineQuery'):
        logger.info(f"on_inline_query: {inline_query}")

    def on_chosen_inline_query(self, client: 'pyrogram.Client', chosen_inline_result: 'types.ChosenInlineResult'):
        logger.info(f"on_chosen_inline_query: {chosen_inline_result}")

    def on_callback_query(self, client: 'pyrogram.Client', callback_query: 'types.CallbackQuery'):
        logger.info(f"on_callback_query: {callback_query}")

    def on_disconnect(self, client: 'pyrogram.Client'):
        logger.info(f"client {client.session_name} disconnected @ {arrow.utcnow()}")

    def deleted_messages_handler(self, client: 'pyrogram.Client', messages: List['types.Message']):
        logger.info(f"deleted_messages_handler: {messages}")
        estimate_date_of_deletion = arrow.utcnow().timestamp()
        for message in messages:
            if message.chat is None:
                # deleted message is from `saved messages`
                message_id = message.message_id
            else:
                # deleted message if from other chats
                message_id = message.message_id
                chat_id: int = message.chat.id
                chat_type: str = message.chat.type

    def run(self) -> None:
        logger.info(mp.current_process().name)
        logger.info(threading.current_thread())

        self.telegram_client.start()

        # register handler based on the type of the client
        if self.telegram_client.client_type == ClientTypes.USER:
            self.telegram_client.add_handler(MessageHandler(self.on_message), group=0)
            self.telegram_client.add_handler(RawUpdateHandler(self.on_raw_update), group=1)
            self.telegram_client.add_handler(DeletedMessagesHandler(self.deleted_messages_handler), group=2)

            # todo: not working, why?
            self.telegram_client.add_handler(ChatMemberUpdatedHandler(self.on_chat_member_updated))

        elif self.telegram_client.client_type == ClientTypes.BOT:
            self.telegram_client.add_handler(MessageHandler(self.on_message))

            # todo: not working, why?
            self.telegram_client.add_handler(DeletedMessagesHandler(self.deleted_messages_handler))

            self.telegram_client.add_handler(InlineQueryHandler(self.on_inline_query))
            self.telegram_client.add_handler(ChosenInlineResultHandler(self.on_chosen_inline_query))
            self.telegram_client.add_handler(CallbackQueryHandler(self.on_callback_query))

            # todo: not working, why?
            self.telegram_client.add_handler(ChatMemberUpdatedHandler(self.on_chat_member_updated))
        else:
            pass
        self.telegram_client.add_handler(DisconnectHandler(self.on_disconnect))

        worker = ClientWorkerThread(
            telegram_client=self.telegram_client,
            index=0,
            db=self.db,
            task_queues=self.task_queues,
        )
        worker.start()

        idle()
        self.telegram_client.stop()


_update = Union[
    raw.types.UpdateBotCallbackQuery, raw.types.UpdateBotInlineQuery, raw.types.UpdateBotInlineSend,
    raw.types.UpdateBotPrecheckoutQuery, raw.types.UpdateBotShippingQuery, raw.types.UpdateBotWebhookJSON,
    raw.types.UpdateBotWebhookJSONQuery, raw.types.UpdateChannel, raw.types.UpdateChannelAvailableMessages,
    raw.types.UpdateChannelMessageForwards, raw.types.UpdateChannelMessageViews, raw.types.UpdateChannelParticipant,
    raw.types.UpdateChannelReadMessagesContents, raw.types.UpdateChannelTooLong, raw.types.UpdateChannelUserTyping,
    raw.types.UpdateChannelWebPage, raw.types.UpdateChat, raw.types.UpdateChatDefaultBannedRights,
    raw.types.UpdateChatParticipantAdd, raw.types.UpdateChatParticipantAdmin, raw.types.UpdateChatParticipantDelete,
    raw.types.UpdateChatParticipants, raw.types.UpdateChatUserTyping, raw.types.UpdateConfig,
    raw.types.UpdateContactsReset, raw.types.UpdateDcOptions, raw.types.UpdateDeleteChannelMessages,
    raw.types.UpdateDeleteMessages, raw.types.UpdateDeleteScheduledMessages, raw.types.UpdateDialogFilter,
    raw.types.UpdateDialogFilterOrder, raw.types.UpdateDialogFilters, raw.types.UpdateDialogPinned,
    raw.types.UpdateDialogUnreadMark, raw.types.UpdateDraftMessage, raw.types.UpdateEditChannelMessage,
    raw.types.UpdateEditMessage, raw.types.UpdateEncryptedChatTyping, raw.types.UpdateEncryptedMessagesRead,
    raw.types.UpdateEncryption, raw.types.UpdateFavedStickers, raw.types.UpdateFolderPeers,
    raw.types.UpdateGeoLiveViewed, raw.types.UpdateGroupCall, raw.types.UpdateGroupCallParticipants,
    raw.types.UpdateInlineBotCallbackQuery, raw.types.UpdateLangPack, raw.types.UpdateLangPackTooLong,
    raw.types.UpdateLoginToken, raw.types.UpdateMessageID, raw.types.UpdateMessagePoll,
    raw.types.UpdateMessagePollVote, raw.types.UpdateNewChannelMessage, raw.types.UpdateNewEncryptedMessage,
    raw.types.UpdateNewMessage, raw.types.UpdateNewScheduledMessage, raw.types.UpdateNewStickerSet,
    raw.types.UpdateNotifySettings, raw.types.UpdatePeerBlocked, raw.types.UpdatePeerLocated,
    raw.types.UpdatePeerSettings, raw.types.UpdatePhoneCall, raw.types.UpdatePhoneCallSignalingData,
    raw.types.UpdatePinnedChannelMessages, raw.types.UpdatePinnedDialogs, raw.types.UpdatePinnedMessages,
    raw.types.UpdatePrivacy, raw.types.UpdatePtsChanged, raw.types.UpdateReadChannelDiscussionInbox,
    raw.types.UpdateReadChannelDiscussionOutbox, raw.types.UpdateReadChannelInbox, raw.types.UpdateReadChannelOutbox,
    raw.types.UpdateReadFeaturedStickers, raw.types.UpdateReadHistoryInbox, raw.types.UpdateReadHistoryOutbox,
    raw.types.UpdateReadMessagesContents, raw.types.UpdateRecentStickers, raw.types.UpdateSavedGifs,
    raw.types.UpdateServiceNotification, raw.types.UpdateStickerSets, raw.types.UpdateStickerSetsOrder,
    raw.types.UpdateTheme, raw.types.UpdateUserName, raw.types.UpdateUserPhone,
    raw.types.UpdateUserPhoto, raw.types.UpdateUserStatus, raw.types.UpdateUserTyping,
    raw.types.UpdateWebPage
]
