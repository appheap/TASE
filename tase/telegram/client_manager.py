import multiprocessing as mp
import threading
from typing import Optional, List, Union

import arrow as arrow
import pyrogram
from pyrogram import types, idle
from pyrogram import raw
from pyrogram.handlers import DisconnectHandler, MessageHandler, RawUpdateHandler

from tase.db.database_client import DatabaseClient
from tase.my_logger import logger
from tase.telegram import TelegramClient
from tase.telegram.client_worker import ClientWorkerThread
from tase.telegram.globals import client_task
from tase.utils import prettify


class ClientManager(mp.Process):
    def __init__(
            self,
            *,
            telegram_client_name: str,
            telegram_client: 'TelegramClient',
            task_queues,
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
        # logger.info(message)
        if client.bot_token is not None:
            logger.info(message)

    def on_raw_update(
            self,
            client: 'pyrogram.Client',
            raw_update: '_update',
            users: List['types.User'],
            chats: List['types.Chat']
    ):
        pass

    @staticmethod
    def on_disconnect(client: 'pyrogram.Client'):
        logger.info(f"client {client.session_name} disconnected @ {arrow.utcnow()}")

    def run(self) -> None:
        logger.info(mp.current_process().name)
        logger.info(threading.current_thread())

        self.telegram_client.start()

        self.telegram_client.add_handler(DisconnectHandler(self.on_disconnect))
        self.telegram_client.add_handler(MessageHandler(self.on_message))
        self.telegram_client.add_handler(RawUpdateHandler(self.on_raw_update))

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