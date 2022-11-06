from collections import defaultdict
from typing import Dict, List, Union

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

# from tase.telegram.client import TelegramClient
from .handler_metadata import HandlerMetadata


class BaseHandler(BaseModel):
    db: DatabaseClient
    telegram_client: object

    class Config:
        arbitrary_types_allowed = True

    def init_handlers(self) -> List[HandlerMetadata]:
        raise NotImplementedError

    async def update_audio_cache(
        self,
        db_audios: Union[List[graph_models.vertices.Audio], List[elasticsearch_models.Audio]],
    ) -> Dict[int, graph_models.vertices.Chat]:
        """
        Update Audio file caches that are not been cached by this telegram client

        Parameters
        ----------
        db_audios : Union[List[graph_models.vertices.Audio], List[elasticsearch_models.Audio]]
            List of audios to be checked
        Returns
        -------
        A dictionary mapping from `chat_id` to a Chat object
        """
        chat_msg = defaultdict(list)
        chats_dict = {}
        for db_audio in db_audios:
            key = db_audio.key if isinstance(db_audio, graph_models.vertices.Audio) else db_audio.id
            if not self.db.document.has_audio_by_key(self.telegram_client.telegram_id, key):
                chat_msg[db_audio.chat_id].append(db_audio.message_id)

            if not chats_dict.get(db_audio.chat_id, None):
                db_chat = self.db.graph.get_chat_by_telegram_chat_id(db_audio.chat_id)

                chats_dict[db_chat.chat_id] = db_chat

        for chat_id, message_ids in chat_msg.items():
            db_chat = chats_dict[chat_id]

            # todo: this approach is only for public channels, what about private channels?
            messages = await self.telegram_client.get_messages(chat_id=db_chat.username, message_ids=message_ids)

            for message in messages:
                self.db.update_or_create_audio(
                    message,
                    self.telegram_client.telegram_id,
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
        hit = self.db.graph.find_hit_by_download_url(hit_download_url)
        if hit is not None:
            audio_vertex = self.db.graph.get_audio_from_hit(hit)
            if audio_vertex is not None:
                es_audio_doc = self.db.index.get_audio_by_id(audio_vertex.key)
                if es_audio_doc:
                    audio_doc = self.db.document.get_audio_by_key(self.telegram_client.telegram_id, es_audio_doc.id)
                    chat = self.db.graph.get_chat_by_telegram_chat_id(es_audio_doc.chat_id)
                    if not audio_doc:
                        # fixme: find a better way of getting messages that have not been cached yet
                        messages = await client.get_messages(chat.username, [es_audio_doc.message_id])
                        if not messages or not len(messages):
                            # todo: could not get the audio from telegram servers, what to do now?
                            logger.error("could not get the audio from telegram servers, what to do now?")
                            return

                        audio, audio_type = get_telegram_message_media_type(messages[0])
                        if audio is None or audio_type == TelegramAudioType.NON_AUDIO:
                            # fixme: instead of raising an exception, it is better to mark the audio file in the
                            #  database as invalid and update related edges and vertices accordingly
                            raise TelegramMessageWithNoAudio(messages[0].id, messages[0].chat.id)
                        else:
                            file_id = audio.file_id
                    else:
                        file_id = audio_doc.file_id

                    from tase.telegram.bots.ui.templates import BaseTemplate
                    from tase.telegram.bots.ui.templates import AudioCaptionData

                    text = BaseTemplate.registry.audio_caption_template.render(
                        AudioCaptionData.parse_from_es_audio_doc(
                            es_audio_doc,
                            from_user,
                            chat,
                            bot_url=f"https://t.me/{(await self.telegram_client.get_me()).username}?start=dl_{hit.download_url}",
                            include_source=True,
                        )
                    )

                    from tase.telegram.bots.ui.inline_buttons.common import (
                        get_audio_markup_keyboard,
                    )

                    status = AudioKeyboardStatus.get_status(
                        self.db,
                        from_user,
                        hit_download_url=hit_download_url,
                    )

                    markup_keyboard = get_audio_markup_keyboard(
                        (await self.telegram_client.get_me()).username,
                        ChatType.BOT,
                        from_user.chosen_language_code,
                        hit.download_url,
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

                    db_download = self.db.graph.create_interaction(
                        hit_download_url,
                        from_user,
                        self.telegram_client.telegram_id,
                        InteractionType.DOWNLOAD,
                        ChatType.BOT,
                    )
                    valid = True
        if not valid:
            # todo: An Error occurred while processing this audio download url, why?
            logger.error(f"An error occurred while processing the download URL for this audio: {hit_download_url}")
            await message.reply_text(
                _trans(
                    "An error occurred while processing the download URL for this audio",
                    from_user.chosen_language_code,
                )
            )
