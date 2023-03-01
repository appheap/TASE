import asyncio
import collections
from collections import defaultdict
from typing import Dict, List, Union, Deque, Tuple, Optional

import pyrogram
from pydantic import BaseModel
from pyrogram.enums import ParseMode
from pyrogram.errors import ChannelInvalid

from tase.common.utils import _trans, async_timed, get_audio_thumbnail_vertices
from tase.db.arangodb import graph as graph_models, document as document_models
from tase.db.arangodb.enums import TelegramAudioType, ChatType, AudioType, AudioInteractionType, PlaylistInteractionType, HitMetadataType
from tase.db.arangodb.helpers import AudioKeyboardStatus
from tase.db.database_client import DatabaseClient
from tase.db.db_utils import get_telegram_message_media_type
from tase.db.elasticsearchdb import models as elasticsearch_models
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
    ) -> Tuple[Dict[int, graph_models.vertices.Chat], Deque[str]]:
        """
        Update Audio file caches that are not been cached by this telegram client

        Parameters
        ----------
        db_audios : Union[Deque[graph_models.vertices.Audio], Deque[elasticsearch_models.Audio]]
            List of audios to be checked
        Returns
        -------
        A dictionary mapping from `chat_id` to a Chat object with list of invalid audios.
        """
        if not db_audios:
            return {}, collections.deque()

        temp = collections.deque()
        temp_keys = collections.deque()
        for db_audio in db_audios:
            if db_audio.key in temp_keys:
                continue

            temp_keys.append(db_audio.key)
            temp.append(db_audio)

        db_audios.clear()
        db_audios.extend(temp)

        chat_msg = defaultdict(set)
        chats_dict: Dict[int, graph_models.vertices.Chat] = {}
        invalid_audio_keys = collections.deque()

        cache_checks = await asyncio.gather(
            *(self.db.document.has_audio_by_key(db_audio.get_doc_cache_key(self.telegram_client.telegram_id)) for db_audio in db_audios)
        )
        db_chats = await asyncio.gather(*(self.db.graph.get_chat_by_telegram_chat_id(db_audio.chat_id) for db_audio in db_audios))

        for cache_check, db_audio in zip(cache_checks, db_audios):
            if not cache_check and not isinstance(cache_check, BaseException):
                chat_msg[db_audio.chat_id].add(db_audio.message_id)

        for db_chat in db_chats:
            if db_chat and db_chat.chat_id not in chats_dict:
                chats_dict[db_chat.chat_id] = db_chat

        # todo: this approach is only for public channels, what about private channels?
        # todo: this might cause `floodwait` errors!, it should be avoided
        async def get_messages(
            chat_id: int,
            message_ids,
        ) -> Tuple[List[pyrogram.types.Message], int]:
            try:
                res = await self.telegram_client.get_messages(chat_id=chats_dict[chat_id].username, message_ids=list(message_ids))
            except KeyError:
                # this chat is no longer is public or available, update the databases accordingly
                if chat_id in chats_dict:
                    chat_v = chats_dict[chat_id]
                else:
                    chat_v = await self.db.graph.get_chat_by_key(str(chat_id))

                if chat_v:
                    if await chat_v.mark_as_invalid():
                        await self.db.mark_chat_audios_as_deleted(chat_id)
                    else:
                        logger.error(f"Error in marking the `Chat` with key `{chat_v.key}` as invalid.")
                return [], chat_id
            except ChannelInvalid:
                if chat_id in chats_dict:
                    chat_v = chats_dict[chat_id]
                else:
                    chat_v = await self.db.graph.get_chat_by_key(str(chat_id))

                if chat_v:
                    if await chat_v.mark_as_invalid():
                        await self.db.mark_chat_audios_as_deleted(chat_id)
                    else:
                        logger.error(f"Error in marking the `Chat` with key `{chat_v.key}` as invalid.")
            else:
                return res, chat_id

        messages_list = await asyncio.gather(*(get_messages(chat_id, message_ids) for chat_id, message_ids in chat_msg.items()))

        messages = [(message, chat_id) for sub_messages_list, chat_id in messages_list if sub_messages_list for message in sub_messages_list if message]
        if messages:
            for message, chat_id in messages:
                thumbs = await get_audio_thumbnail_vertices(self.db, self.telegram_client, message)
                await self.db.update_or_create_audio(
                    message,
                    self.telegram_client.telegram_id,
                    chat_id,
                    AudioType.NOT_ARCHIVED,
                    chats_dict[chat_id].get_chat_scores(),
                    thumbs,
                )

        return chats_dict, invalid_audio_keys

    async def validate_audio_vertex(
        self,
        audio_vertex: graph_models.vertices.Audio,
        client: pyrogram.Client,
        from_user_id: int,
        chat_type: ChatType,
    ) -> bool:
        if not audio_vertex:
            # todo: translate this string
            if chat_type == ChatType.BOT:
                await client.send_message(
                    from_user_id,
                    "This `download_url` is no longer valid!",
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )
            return False

        if not audio_vertex.is_usable():
            # todo: translate this string
            if chat_type == ChatType.BOT:
                await client.send_message(
                    from_user_id,
                    "This `download_url` is no longer valid, probably the channel has deleted this audio!",
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )
            return False

        return True

    async def get_audio_file_id(
        self,
        from_user: graph_models.vertices.User,
        audio_vertex: graph_models.vertices.Audio,
        client: pyrogram.Client,
        chat_type: ChatType,
    ) -> Tuple[graph_models.vertices.Chat, Optional[str]]:
        # todo: handle exceptions
        audio_doc, chat = await asyncio.gather(
            *(
                self.db.document.get_audio_by_key(audio_vertex.get_doc_cache_key(self.telegram_client.telegram_id)),
                self.db.graph.get_chat_by_telegram_chat_id(audio_vertex.chat_id),
            )
        )

        chat: graph_models.vertices.Chat = chat

        if isinstance(audio_doc, document_models.Audio):  # fixme: check for `BaseException` type
            return chat, audio_doc.file_id
        else:
            # fixme: find a better way of getting messages that have not been cached yet
            try:
                if await self.telegram_client.peer_exists(audio_vertex.chat_id):
                    messages = await self.telegram_client.get_messages(audio_vertex.chat_id, [audio_vertex.message_id])
                else:
                    messages = await self.telegram_client.get_messages(chat.username, [audio_vertex.message_id])
            except KeyError:
                # todo: this chat is no longer is public or available, update the databases accordingly
                if chat_type == ChatType.BOT:
                    await client.send_message(
                        from_user.user_id,
                        "The sender chat of the message containing this audio does not exist anymore, " "please try again!",
                    )

                logger.error("The sender chat of the message containing this audio does not exist anymore, please try again!")
                return chat, None
            except Exception as e:
                logger.exception(e)
                messages = None

            if not messages:
                # todo: could not get the audio from telegram servers, what to do now?
                if chat_type == ChatType.BOT:
                    await client.send_message(
                        from_user.user_id,
                        _trans(
                            "An error occurred while processing the download URL for this audio",
                            from_user.chosen_language_code,
                        ),
                    )

                logger.error("could not get the audio from telegram servers, what to do now?")
                return chat, None

            thumbnail_vertices = await get_audio_thumbnail_vertices(self.db, self.telegram_client, messages)

            # update the audio in all databases
            await self.db.update_or_create_audio(
                messages[0],
                self.telegram_client.telegram_id,
                audio_vertex.chat_id,
                AudioType.NOT_ARCHIVED,
                chat.get_chat_scores(),
                thumbnail_vertices,
            )

            audio, audio_type = get_telegram_message_media_type(messages[0])
            if audio is None or audio_type == TelegramAudioType.NON_AUDIO:
                # invalidate audio vertices and remove the not-archived ones from all playlists.
                await self.db.invalidate_old_audios(
                    chat_id=audio_vertex.chat_id,
                    message_id=audio_vertex.message_id,
                )

                if chat_type == ChatType.BOT:
                    # todo: translate this text string.
                    await client.send_message(
                        from_user.user_id,
                        "This message containing this audio does not exist anymore, please try again!",
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=True,
                    )
                return chat, None
            else:
                return chat, audio.file_id

    @async_timed()
    async def download_audio(
        self,
        client: pyrogram.Client,
        from_user: graph_models.vertices.User,
        hit_download_url: str,
        message: pyrogram.types.Message,
        from_deep_link: bool,
    ) -> None:
        """
        Download the audio file from the given download link and send it the user.

        Parameters
        ----------
        client : pyrogram.Client
            Client receiving this update.
        from_user : graph_models.vertices.User
            User to send the audio file to.
        hit_download_url : str
            Download URL of the hit vertex.
        message : pyrogram.types.Message
            Telegram message where the request initiated from.
        from_deep_link : bool
            Whether the download URL is a deep link or not.

        """
        if not client or not from_user or not hit_download_url:
            return

        # todo: handle errors for invalid messages
        hit = await self.db.graph.find_hit_by_download_url(hit_download_url)
        if not hit:
            await message.reply_text(
                "This `download_url` is no valid!",
                quote=True,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
            return

        audio_vertex = await self.db.graph.get_audio_from_hit_download_url(hit_download_url)

        if not await self.validate_audio_vertex(audio_vertex, client, from_user.user_id, ChatType.BOT):
            return

        if from_deep_link:
            sender_user_vertex = await self.db.graph.get_audio_link_sender(hit_download_url)
            if sender_user_vertex:
                if from_user.user_id != sender_user_vertex.user_id:
                    # The user requesting this audio is not the user who has queried the audio in the first place, thus, it can be inferred that the audio
                    # has been shared with him/her by another user.

                    # todo: do not create share interaction if one has already been created recently.
                    await self.db.graph.create_audio_interaction(
                        sender_user_vertex,
                        self.telegram_client.telegram_id,
                        AudioInteractionType.SHARE_AUDIO,
                        ChatType.BOT,
                        hit_download_url,
                    )
            else:
                # todo: check for SPAM
                pass
        else:
            # Check whether the user requesting this audio has initiated the search query earlier.
            if not await self.db.graph.user_has_initiated_query(from_user, hit_download_url):
                await message.reply_text(
                    "This `download_url` is no valid for you!",
                    quote=True,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )
                return

        chat, file_id = await self.get_audio_file_id(from_user, audio_vertex, client, ChatType.BOT)
        if not chat or not file_id:
            return

        from tase.telegram.bots.ui.templates import BaseTemplate
        from tase.telegram.bots.ui.templates import AudioCaptionData
        from tase.telegram.bots.ui.inline_buttons.common import get_audio_markup_keyboard

        text = BaseTemplate.registry.audio_caption_template.render(
            AudioCaptionData.parse_from_audio(
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
            status,
            hit.metadata.playlist_vertex_key if hit.metadata else None,
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

        if not hit.metadata:
            # the hit doesn't have metadata, consider it as inline/non-inline search
            if await self.db.graph.get_audio_interaction_by_user(
                from_user,
                hit_download_url,
                AudioInteractionType.DOWNLOAD_AUDIO,
            ):
                audio_int_type = AudioInteractionType.REDOWNLOAD_AUDIO
            else:
                audio_int_type = AudioInteractionType.DOWNLOAD_AUDIO

            await self.db.graph.create_audio_interaction(
                from_user,
                self.telegram_client.telegram_id,
                audio_int_type,
                ChatType.BOT,
                hit_download_url,
            )

            return

        audio_int_type = None
        playlist_int_type = None

        if hit.metadata.type_ == HitMetadataType.AUDIO:
            # link came from an inline/non-inline search
            if await self.db.graph.get_audio_interaction_by_user(
                from_user,
                hit_download_url,
                AudioInteractionType.DOWNLOAD_AUDIO,
            ):
                audio_int_type = AudioInteractionType.REDOWNLOAD_AUDIO
            else:
                audio_int_type = AudioInteractionType.DOWNLOAD_AUDIO
        elif hit.metadata.type_ == HitMetadataType.PLAYLIST_AUDIO:
            playlist = await self.db.graph.get_playlist_by_key(hit.metadata.playlist_key)
            if playlist and await self.db.graph.audio_is_or_was_in_playlist(audio_vertex.key, playlist.key):
                if await self.db.graph.get_playlist_audio_interaction_by_user(
                    from_user,
                    hit_download_url,
                    playlist.key,
                    PlaylistInteractionType.DOWNLOAD_AUDIO,
                ):
                    playlist_int_type = PlaylistInteractionType.REDOWNLOAD_AUDIO
                else:
                    playlist_int_type = PlaylistInteractionType.DOWNLOAD_AUDIO

                if await self.db.graph.get_audio_interaction_by_user(
                    from_user,
                    hit_download_url,
                    AudioInteractionType.DOWNLOAD_AUDIO,
                ):
                    audio_int_type = AudioInteractionType.REDOWNLOAD_AUDIO
                else:
                    audio_int_type = AudioInteractionType.DOWNLOAD_AUDIO
        else:
            pass

        if audio_int_type:
            await self.db.graph.create_audio_interaction(
                from_user,
                self.telegram_client.telegram_id,
                audio_int_type,
                ChatType.BOT,
                hit_download_url,
            )

        if playlist_int_type:
            await self.db.graph.create_playlist_interaction(
                from_user,
                self.telegram_client.telegram_id,
                playlist_int_type,
                ChatType.BOT,
                hit.metadata.playlist_key,
                audio_hit_download_url=hit_download_url,
            )

    async def on_inline_audio_article_item_clicked(
        self,
        from_user: graph_models.vertices.User,
        client: pyrogram.Client,
        chat_type: ChatType,
        hit_download_url: str,
        playlist_key: Optional[str] = None,
    ) -> None:
        audio_vertex = await self.db.graph.get_audio_from_hit_download_url(hit_download_url)
        if not await self.validate_audio_vertex(audio_vertex, client, from_user.user_id, chat_type):
            return

        chat, file_id = await self.get_audio_file_id(from_user, audio_vertex, client, chat_type)
        if not chat or not file_id:
            return

        if chat_type == ChatType.BOT:
            from tase.db.arangodb.helpers import AudioKeyboardStatus
            from tase.telegram.bots.ui.inline_buttons.common import get_audio_markup_keyboard
            from tase.telegram.bots.ui.templates import BaseTemplate, AudioCaptionData

            text = BaseTemplate.registry.audio_caption_template.render(
                AudioCaptionData.parse_from_audio(
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
                chat_type,
                from_user.chosen_language_code,
                hit_download_url,
                status,
                playlist_key=playlist_key,
            )

            if audio_vertex.audio_type == TelegramAudioType.AUDIO_FILE:
                await client.send_audio(
                    chat_id=from_user.user_id,
                    audio=file_id,
                    caption=text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=markup_keyboard,
                )
            else:
                await client.send_document(
                    chat_id=from_user.user_id,
                    document=file_id,
                    caption=text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=markup_keyboard,
                )

    async def update_audio_keyboard_markup(
        self,
        client: pyrogram.Client,
        from_user: graph_models.vertices.User,
        telegram_chosen_inline_result: pyrogram.types.ChosenInlineResult,
        hit_download_url: str,
        chat_type: ChatType,
        playlist_key: Optional[str] = None,
    ):
        retry_left = 5
        audio_vertex = None

        while retry_left:
            audio_vertex = await self.db.graph.get_audio_from_hit_download_url(hit_download_url)
            if not audio_vertex:
                retry_left -= 1

                # fixme: this should not happen
                logger.error("This should not happen")
                await asyncio.sleep(2)

                continue

            break

        if not audio_vertex:
            logger.error("This should not happen at all!")
            # fixme: this should not happen at all!
            return

        from tase.telegram.bots.ui.inline_buttons.common import get_audio_markup_keyboard

        status = await AudioKeyboardStatus.get_status(
            self.db,
            from_user,
            audio_vertex_key=audio_vertex.key,
        )

        await client.edit_inline_reply_markup(
            telegram_chosen_inline_result.inline_message_id,
            reply_markup=get_audio_markup_keyboard(
                (await self.telegram_client.get_me()).username,
                chat_type,
                from_user.chosen_language_code,
                hit_download_url,
                status,
                playlist_key=playlist_key,
            ),
        )

    async def update_audio_doc_coming_in_from_archive_channel(
        self,
        message: pyrogram.types.Message,
    ):
        if message.chat and message.chat.id == self.telegram_client.archive_channel_info.chat_id:
            # logger.debug(f"Archiving audio in client `{self.telegram_client.name}` ...")
            audio_doc = await self.db.document.update_or_create_audio(
                message,
                telegram_client_id=self.telegram_client.telegram_id,
                chat_id=self.telegram_client.archive_channel_info.chat_id,
            )
            if not audio_doc:
                logger.error(f"Error in creating audio doc for message ID `{message.id}` in client `{self.telegram_client.name}`")
