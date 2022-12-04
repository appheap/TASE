import asyncio
import collections
from collections import defaultdict
from typing import Dict, List, Union, Deque

import pyrogram
from pydantic import BaseModel
from pyrogram.enums import ParseMode

from tase.common.utils import _trans, async_timed
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.enums import TelegramAudioType, InteractionType, ChatType
from tase.db.arangodb.helpers import AudioKeyboardStatus
from tase.db.database_client import DatabaseClient
from tase.db.db_utils import get_telegram_message_media_type
from tase.db.elasticsearchdb import models as elasticsearch_models
from tase.errors import TelegramMessageWithNoAudio
from tase.my_logger import logger
from tase.telegram.client import TelegramClient
from .handler_metadata import HandlerMetadata


class BaseHandler(BaseModel):
    db: DatabaseClient
    telegram_client: TelegramClient

    class Config:
        arbitrary_types_allowed = True

    def init_handlers(self) -> List[HandlerMetadata]:
        raise NotImplementedError

    @async_timed()
    async def update_audio_cache(
        self,
        db_audios: Union[Deque[graph_models.vertices.Audio], Deque[elasticsearch_models.Audio]],
    ) -> Dict[int, graph_models.vertices.Chat]:
        """
        Update Audio file caches that are not been cached by this telegram client

        Parameters
        ----------
        db_audios : Union[Deque[graph_models.vertices.Audio], Deque[elasticsearch_models.Audio]]
            List of audios to be checked
        Returns
        -------
        A dictionary mapping from `chat_id` to a Chat object
        """
        chat_msg = defaultdict(collections.deque)
        chats_dict = {}

        def get_key(_db_audio) -> str:
            return _db_audio.key if isinstance(_db_audio, graph_models.vertices.Audio) else _db_audio.id

        cache_check_task = (self.db.document.has_audio_by_key(self.telegram_client.telegram_id, get_key(db_audio)) for db_audio in db_audios)
        db_chats_task = (self.db.graph.get_chat_by_telegram_chat_id(db_audio.chat_id) for db_audio in db_audios)

        cache_checks = await asyncio.gather(*cache_check_task)
        db_chats = await asyncio.gather(*db_chats_task)

        [chat_msg[db_audio.chat_id].append(db_audio.message_id) for cache_check, db_audio in zip(cache_checks, db_audios) if not cache_check]

        for db_chat in db_chats:
            if db_chat.chat_id not in chats_dict:
                chats_dict[db_chat.chat_id] = db_chat

        # todo: this approach is only for public channels, what about private channels?
        # todo: this might cause `floodwait` errors!, it should be avoided
        messages_list = await asyncio.gather(
            *(self.telegram_client.get_messages(chat_id=chats_dict[chat_id].username, message_ids=message_ids) for chat_id, message_ids in chat_msg.items())
        )

        await asyncio.gather(
            *(
                self.db.update_or_create_audio(
                    message,
                    self.telegram_client.telegram_id,
                )
                for sub_messages_list in messages_list
                for message in sub_messages_list
            )
        )

        return chats_dict

    @async_timed()
    async def download_audio(
        self,
        client: pyrogram.Client,
        from_user: graph_models.vertices.User,
        text: str,
        message: pyrogram.types.Message,
    ):
        if client is None or from_user is None or text is None or not len(text) or message is None:
            return

        valid = False
        # todo: handle errors for invalid messages
        hit_download_url = text.split("dl_")[1]
        audio_vertex = await self.db.graph.get_audio_from_hit_download_url(hit_download_url)

        if audio_vertex is not None:
            db_download_task = asyncio.create_task(
                self.db.graph.create_interaction(
                    hit_download_url,
                    from_user,
                    self.telegram_client.telegram_id,
                    InteractionType.DOWNLOAD,
                    ChatType.BOT,
                )
            )

            # todo: handle exceptions
            audio_doc, chat = await asyncio.gather(
                *(
                    self.db.document.get_audio_by_key(
                        self.telegram_client.telegram_id,
                        audio_vertex.key,
                    ),
                    self.db.graph.get_chat_by_telegram_chat_id(audio_vertex.chat_id),
                )
            )

            update_audio_task = None
            if audio_doc:
                file_id = audio_doc.file_id
            else:
                # fixme: find a better way of getting messages that have not been cached yet
                messages = await client.get_messages(chat.username, [audio_vertex.message_id])
                if not messages or not len(messages):
                    # todo: could not get the audio from telegram servers, what to do now?
                    logger.error("could not get the audio from telegram servers, what to do now?")
                    return

                # update the audio in all databases
                update_audio_task = asyncio.create_task(self.db.update_or_create_audio(messages[0], self.telegram_client.telegram_id))

                audio, audio_type = get_telegram_message_media_type(messages[0])
                if audio is None or audio_type == TelegramAudioType.NON_AUDIO:
                    # fixme: instead of raising an exception, it is better to mark the audio file in the
                    #  database as invalid and update related edges and vertices accordingly
                    raise TelegramMessageWithNoAudio(messages[0].id, messages[0].chat.id)
                else:
                    file_id = audio.file_id

            from tase.telegram.bots.ui.templates import BaseTemplate
            from tase.telegram.bots.ui.templates import AudioCaptionData
            from tase.telegram.bots.ui.inline_buttons.common import get_audio_markup_keyboard

            text = BaseTemplate.registry.audio_caption_template.render(
                AudioCaptionData.parse_from_audio_vertex(
                    audio_vertex,
                    from_user,
                    chat,
                    bot_url=f"https://t.me/{(await self.telegram_client.get_me()).username}?start=dl_{hit_download_url}",
                    include_source=True,
                )
            )

            status = await AudioKeyboardStatus.get_status(
                self.db,
                from_user,
                hit_download_url=hit_download_url,
            )

            markup_keyboard = get_audio_markup_keyboard(
                (await self.telegram_client.get_me()).username,
                ChatType.BOT,
                from_user.chosen_language_code,
                hit_download_url,
                audio_vertex.valid_for_inline_search,
                status,
            )

            if audio_vertex.audio_type == TelegramAudioType.AUDIO_FILE:
                await message.reply_audio(
                    audio=file_id,
                    caption=text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=markup_keyboard,
                )
            else:
                await message.reply_document(
                    document=file_id,
                    caption=text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=markup_keyboard,
                )

            valid = True

            await db_download_task
            if update_audio_task:
                await update_audio_task

        if not valid:
            # todo: An Error occurred while processing this audio download url, why?
            logger.error(f"An error occurred while processing the download URL for this audio: {hit_download_url}")
            await message.reply_text(
                _trans(
                    "An error occurred while processing the download URL for this audio",
                    from_user.chosen_language_code,
                )
            )
