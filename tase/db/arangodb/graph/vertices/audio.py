from __future__ import annotations

import asyncio
import collections
import copy
from typing import Optional, List, Generator, TYPE_CHECKING, Deque, Tuple

import pyrogram

from aioarango.models import PersistentIndex
from tase.common.preprocessing import clean_text, empty_to_null
from tase.common.utils import (
    datetime_to_timestamp,
    get_now_timestamp,
    find_hashtags_in_text,
)
from tase.db.db_utils import (
    get_telegram_message_media_type,
    parse_audio_key,
    is_audio_valid_for_inline,
    parse_audio_document_key_from_raw_attributes,
)
from tase.db.helpers import ChatScores
from tase.errors import (
    TelegramMessageWithNoAudio,
    InvalidToVertex,
    InvalidFromVertex,
    EdgeCreationFailed,
)
from tase.my_logger import logger
from .base_vertex import BaseVertex
from .hashtag import Hashtag
from .hit import Hit
from .interaction import Interaction
from .user import User
from ...helpers import BitRateType

if TYPE_CHECKING:
    from .. import ArangoGraphMethods
from ...enums import TelegramAudioType, MentionSource, InteractionType, AudioType


class Audio(BaseVertex):
    __collection_name__ = "audios"
    schema_version = 1
    __indexes__ = [
        PersistentIndex(
            custom_version=1,
            name="chat_id",
            fields=[
                "chat_id",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="message_id",
            fields=[
                "message_id",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="message_date",
            fields=[
                "message_date",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="message_edit_date",
            fields=[
                "message_edit_date",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="views",
            fields=[
                "views",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="forward_date",
            fields=[
                "forward_date",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="via_bot",
            fields=[
                "via_bot",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="has_protected_content",
            fields=[
                "has_protected_content",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="file_unique_id",
            fields=[
                "file_unique_id",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="date",
            fields=[
                "date",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="audio_type",
            fields=[
                "audio_type",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="valid_for_inline_search",
            fields=[
                "valid_for_inline_search",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="estimated_bit_rate_type",
            fields=[
                "estimated_bit_rate_type",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="has_checked_forwarded_message",
            fields=[
                "has_checked_forwarded_message",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="has_checked_forwarded_message_at",
            fields=[
                "has_checked_forwarded_message_at",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="type",
            fields=[
                "type",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="is_forwarded",
            fields=[
                "is_forwarded",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="is_deleted",
            fields=[
                "is_deleted",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="deleted_at",
            fields=[
                "deleted_at",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="is_edited",
            fields=[
                "is_edited",
            ],
        ),
    ]

    __non_updatable_fields__ = [
        "has_checked_forwarded_message_at",
        "deleted_at",
        "archive_chat_id",
        "archive_message_id",
    ]

    chat_id: int
    message_id: int
    message_caption: Optional[str]
    raw_message_caption: Optional[str]
    message_date: Optional[int]
    message_edit_date: Optional[int]
    views: Optional[int]
    forward_date: Optional[int]
    forward_from_user_id: Optional[int]
    forward_from_chat_id: Optional[int]
    forward_from_message_id: Optional[int]
    forward_signature: Optional[str]
    forward_sender_name: Optional[str]
    via_bot: bool
    has_protected_content: Optional[bool]
    # forward_from_chat : forward_from => Chat
    # forward_from : forward_from => Chat
    # via_bot : via_bot => User

    file_unique_id: Optional[str]
    duration: Optional[int]
    performer: Optional[str]
    raw_performer: Optional[str]
    title: Optional[str]
    raw_title: Optional[str]
    file_name: Optional[str]
    raw_file_name: Optional[str]
    mime_type: Optional[str]
    file_size: Optional[int]
    date: Optional[int]

    ####################################################
    audio_type: TelegramAudioType  # whether the audio file is shown in the `audios` or `files/documents` section of telegram app
    valid_for_inline_search: bool
    """
     when an audio's title is None or the audio is shown in document section of
     telegram, then that audio could not be shown in telegram inline mode. Moreover, it should not have keyboard
     markups like `add_to_playlist`, etc... . On top of that, if any audio of this kind gets downloaded through
     query search, then, it cannot be shown in `download_history` section or any other sections that work in inline
     mode.
    """

    estimated_bit_rate_type: BitRateType
    has_checked_forwarded_message: Optional[bool]
    has_checked_forwarded_message_at: Optional[int]

    type: AudioType
    archive_chat_id: Optional[int]
    archive_message_id: Optional[int]

    chat_audio_indexer_score: Optional[float]
    chat_audio_doc_indexer_score: Optional[float]
    chat_username_extractor_score: Optional[float]

    is_forwarded: bool
    is_deleted: bool
    deleted_at: Optional[int]  # this is not always accurate
    is_edited: bool

    @classmethod
    def parse_key(
        cls,
        telegram_message: pyrogram.types.Message,
        chat_id: int,
    ) -> Optional[str]:
        """
        Parse the `key` from the given `telegram_message` argument

        Parameters
        ----------
        telegram_message : pyrogram.types.Message
            Telegram message to parse the key from
        chat_id : int
            Chat ID this message belongs to.

        Returns
        -------
        str, optional
            Parsed key if the parsing was successful, otherwise return `None` if the `telegram_message` is `None`.

        Raises
        ------
        TelegramMessageWithNoAudio
            If `telegram_message` argument does not contain any valid audio file.
        """
        return parse_audio_key(telegram_message, chat_id)

    @classmethod
    def parse(
        cls,
        telegram_message: pyrogram.types.Message,
        chat_id: int,
        audio_type: AudioType,
        chat_scores: ChatScores,
    ) -> Optional[Audio]:
        """
        Parse an `Audio` from the given `telegram_message` argument.

        Parameters
        ----------
        telegram_message : pyrogram.types.Message
            Telegram message to parse the `Audio` from
        chat_id : int
            Chat ID this message belongs to.
        audio_type : AudioType
            Type of the audio.
        chat_scores : ChatScores
            Scores of the parent chat.

        Returns
        -------
        Audio, optional
            Parsed `Audio` if parsing was successful, otherwise, return `None`.

        Raises
        ------
        TelegramMessageWithNoAudio
            If `telegram_message` argument does not contain any valid audio file.
        """
        if telegram_message is None:
            return None

        key = Audio.parse_key(telegram_message, chat_id)
        if not key:
            return None

        audio, telegram_audio_type = get_telegram_message_media_type(telegram_message)
        if audio is None or telegram_audio_type == TelegramAudioType.NON_AUDIO:
            raise TelegramMessageWithNoAudio(telegram_message.id, chat_id)

        title = getattr(audio, "title", None)

        valid_for_inline = is_audio_valid_for_inline(audio, telegram_audio_type)

        is_forwarded = True if telegram_message.forward_date else False

        if telegram_message.forward_from_chat:
            forwarded_from_chat_id = telegram_message.forward_from_chat.id
        else:
            forwarded_from_chat_id = None

        if telegram_message.forward_from:
            forwarded_from_user_id = telegram_message.forward_from.id
        else:
            forwarded_from_user_id = None

        if is_forwarded and forwarded_from_chat_id is not None:
            has_checked_forwarded_message = False
        else:
            has_checked_forwarded_message = None

        raw_title = copy.copy(title)
        raw_caption = copy.copy(telegram_message.caption if telegram_message.caption else telegram_message.text)
        raw_performer = copy.copy(getattr(audio, "performer", None))
        raw_file_name = copy.copy(audio.file_name)

        title = clean_text(title)
        caption = clean_text(telegram_message.caption if telegram_message.caption else telegram_message.text)
        performer = clean_text(getattr(audio, "performer", None))
        file_name = clean_text(audio.file_name)

        duration = getattr(audio, "duration", None)

        return Audio(
            key=key,
            chat_id=telegram_message.chat.id,
            message_id=telegram_message.id,
            message_caption=caption,
            raw_message_caption=raw_caption,
            message_date=datetime_to_timestamp(telegram_message.date),
            message_edit_date=datetime_to_timestamp(telegram_message.edit_date),
            views=telegram_message.views,
            forward_date=datetime_to_timestamp(telegram_message.forward_date),
            forward_from_user_id=forwarded_from_user_id,
            forward_from_chat_id=forwarded_from_chat_id,
            forward_from_message_id=telegram_message.forward_from_message_id,
            forward_signature=telegram_message.forward_signature,
            forward_sender_name=telegram_message.forward_sender_name,
            via_bot=True if telegram_message.via_bot else False,
            has_protected_content=telegram_message.has_protected_content,
            ################################
            file_unique_id=audio.file_unique_id,
            duration=duration,
            performer=performer,
            raw_performer=empty_to_null(raw_performer),
            title=title,
            raw_title=empty_to_null(raw_title),
            file_name=file_name,
            raw_file_name=empty_to_null(raw_file_name),
            mime_type=audio.mime_type,
            file_size=audio.file_size,
            date=datetime_to_timestamp(audio.date),
            ################################
            valid_for_inline_search=valid_for_inline,
            estimated_bit_rate_type=BitRateType.estimate(
                audio.file_size,
                duration,
            ),
            audio_type=telegram_audio_type,
            has_checked_forwarded_message=has_checked_forwarded_message,
            type=audio_type,
            chat_audio_indexer_score=chat_scores.audio_indexer_score,
            chat_audio_doc_indexer_score=chat_scores.audio_doc_indexer_score,
            chat_username_extractor_score=chat_scores.username_extractor_score,
            is_forwarded=is_forwarded,
            is_deleted=True if telegram_message.empty else False,
            is_edited=True if telegram_message.edit_date else False,
        )

    async def mark_as_deleted(self) -> bool:
        """
        Mark the Audio the as deleted. This happens when the message is deleted in telegram.

        Returns
        -------
        bool
            Whether the operation was successful or not.

        """
        self_copy = self.copy(deep=True)
        self_copy.is_deleted = True
        self_copy.deleted_at = get_now_timestamp()
        return await self.update(
            self_copy,
            reserve_non_updatable_fields=False,
            check_for_revisions_match=False,
        )

    async def mark_as_non_audio(self) -> bool:
        """
        Mark the audio as invalid since it has been edited in telegram and changed to non-audio file.


        Returns
        -------
        bool
            Whether the update was successful or not.

        """
        self_copy = self.copy(deep=True)
        self_copy.audio_type = TelegramAudioType.NON_AUDIO
        return await self.update(
            self_copy,
            reserve_non_updatable_fields=True,
            check_for_revisions_match=False,
        )

    async def mark_as_archived(
        self,
        archive_chat_id: int,
        archive_message_id: int,
    ) -> bool:
        """
        Mark the audio as archived after it has been archived.

        Parameters
        ----------
        archive_chat_id : int
            ID of the archive channel.
        archive_message_id : int
            ID of the message in the archive channel.


        Returns
        -------
        bool
            Whether the update was successful or not.
        """
        if archive_chat_id is None or archive_message_id is None:
            return False

        self_copy: Audio = self.copy(deep=True)
        self_copy.type = AudioType.ARCHIVED
        self_copy.archive_chat_id = archive_chat_id
        self_copy.archive_message_id = archive_message_id

        return await self.update(
            self_copy,
            reserve_non_updatable_fields=False,
            check_for_revisions_match=False,
        )

    @property
    def is_archived(self) -> bool:
        """
        Check if this audio is archived or not.

        Returns
        -------
        bool
            Whether this audio is archived or not.

        """
        return self.type == AudioType.ARCHIVED

    def is_usable(
        self,
        check_for_inline_mode: bool = False,
    ) -> bool:
        """
        Check if whether this audio vertex is usable to be sent to user.

        Parameters
        ----------
        check_for_inline_mode : bool, default : False
            Whether this audio is being sent in inline mode or not.

        Returns
        -------
        bool
            Whether the audio vertex is usable for sending or not.
        """
        # todo: add more checks if audio attributes are updated.
        if check_for_inline_mode and not self.valid_for_inline_search:
            return False

        if self.type in (AudioType.ARCHIVED, AudioType.UPLOADED, AudioType.SENT_BY_USERS):
            return True

        if self.is_deleted or self.audio_type == TelegramAudioType.NON_AUDIO:
            return False

        return True

    def get_doc_cache_key(
        self,
        telegram_client_id: int,
    ) -> Optional[str]:
        if not telegram_client_id:
            return None

        if self.type == AudioType.NOT_ARCHIVED:
            return parse_audio_document_key_from_raw_attributes(telegram_client_id, self.chat_id, self.message_id, self.file_unique_id)
        else:
            return parse_audio_document_key_from_raw_attributes(telegram_client_id, self.archive_chat_id, self.archive_message_id, self.file_unique_id)

    def find_hashtags(self) -> List[Tuple[str, int, MentionSource]]:
        """
        Find hashtags in text attributes of this audio vertex.

        Returns
        -------
        list
            A list containing a tuple of the `hashtag` string, its starting index, and its mention source.

        Raises
        ------
        ValueError
            If input data is invalid.
        """
        return find_hashtags_in_text(
            [
                self.raw_message_caption,
                self.raw_title,
                self.raw_performer,
                self.raw_file_name,
            ],
            [
                MentionSource.MESSAGE_TEXT,
                MentionSource.AUDIO_TITLE,
                MentionSource.AUDIO_PERFORMER,
                MentionSource.AUDIO_FILE_NAME if self.audio_type == TelegramAudioType.AUDIO_FILE else MentionSource.DOCUMENT_FILE_NAME,
            ],
        )


######################################################################


class AudioMethods:
    _get_audio_from_hit_query = (
        "for v,e in 1..1 outbound @start_vertex graph @graph_name options {order:'dfs', edgeCollections:[@has], vertexCollections:[@audios]}"
        "   limit 1"
        "   return v"
    )

    _check_audio_validity_for_inline_mode_by_hit_download_url = (
        "for hit in @@hits"
        "   filter hit.download_url == @hit_download_url"
        "   for v,e in 1..1 outbound hit graph @graph_name options {order:'dfs', edgeCollections:[@has], vertexCollections:[@audios]}"
        "       limit 1"
        "       return v.valid_for_inline_search"
    )

    _get_audio_by_hit_download_url = (
        "for hit in @@hits"
        "   filter hit.download_url == @hit_download_url"
        "   for v,e in 1..1 outbound hit graph @graph_name options {order:'dfs', edgeCollections:[@has], vertexCollections:[@audios]}"
        "       limit 1"
        "       return v"
    )

    _get_user_download_history_query = (
        "for dl_v,dl_e in 1..1 outbound @start_vertex graph @graph_name options {order:'dfs', edgeCollections:[@has], vertexCollections:[@interactions]}"
        "   filter dl_v.type == @interaction_type"
        "   sort dl_e.created_at DESC"
        "   for aud_v,has_e in 1..1 outbound dl_v graph @graph_name options {order:'dfs', edgeCollections:[@has], vertexCollections:[@audios]}"
        "       filter not aud_v.is_deleted or aud_v.type in @archived_lst"
        "       limit @offset, @limit"
        "       return aud_v"
    )

    _get_user_download_history_inline_query = (
        "for dl_v,dl_e in 1..1 outbound @start_vertex graph @graph_name options {order:'dfs', edgeCollections:[@has], vertexCollections:[@interactions]}"
        "   filter dl_v.type == @interaction_type"
        "   sort dl_e.created_at DESC"
        "   for aud_v,has_e in 1..1 outbound dl_v graph @graph_name options {order:'dfs', edgeCollections:[@has], vertexCollections:[@audios]}"
        "       filter (not aud_v.is_deleted or aud_v.type in @archived_lst) and aud_v.valid_for_inline_search == true"
        "       limit @offset, @limit"
        "       return aud_v"
    )

    _get_audios_by_keys = "return document(@@audios, @audio_keys)"

    _get_not_deleted_audios_by_chat_id_and_message_id = (
        "for audio in @@audios"
        "   filter audio.chat_id == @chat_id and not audio.is_deleted and audio.message_id == @message_id and audio._key != @excluded_key"
        "   sort audio.created_at asc"
        "   return audio"
    )

    _mark_old_audios_as_deleted_by_chat_id_and_message_id_with_excluded_key = (
        "for audio in @@audios"
        "   filter audio.chat_id == @chat_id and not audio.is_deleted and audio.message_id == @message_id and audio._key != @excluded_key"
        "   sort audio.created_at asc"
        "   update {_key:audio._key, is_deleted: true, deleted_at: @deleted_at, modified_at: @deleted_at} in audios options {ignoreRevs: true}"
        "   filter NEW.type == @not_archived"
        "   return NEW"
    )

    _mark_old_audios_as_deleted_by_chat_id_and_message_id_without_excluded_key = (
        "for audio in @@audios"
        "   filter audio.chat_id == @chat_id and not audio.is_deleted and audio.message_id == @message_id "
        "   sort audio.created_at asc"
        "   update {_key:audio._key, is_deleted: true, deleted_at: @deleted_at, modified_at: @deleted_at} in audios options {ignoreRevs: true}"
        "   filter NEW.type == @not_archived"
        "   return NEW"
    )

    _remove_audio_from_all_playlists_query = (
        "for v,e in 1..1 inbound @audio_vertex_id graph @graph_name options {order: 'dfs', edgeCollections: [@has], vertexCollections: [@playlists]}"
        "   remove e in @@has_"
    )

    _iter_audios_query = "for audio in @@audios" "   filter audio.modified_at <= @now" "   sort audio.created_at asc" "   return audio"

    _get_new_indexed_audios_count_query = (
        "for audio in @@audios"
        "   filter audio.created_at >= @checkpoint"
        "   collect with count into new_indexed_audios_count"
        "   return new_indexed_audios_count"
    )

    _get_total_indexed_audios_count_query = (
        "for audio in @@audios" "   collect with count into total_indexed_audios_count" "   return total_indexed_audios_count"
    )

    # fixme: this query returns duplicate items in the same group
    _get_not_archived_downloaded_audios = (
        "for interaction in @@interactions"
        "   filter interaction.type == @interaction_type and interaction.created_at < @now"
        "   sort interaction.created_at desc"
        "   for v_audio in 1..1 outbound interaction graph @graph_name options {order: 'dfs', edgeCollections: [@has], vertexCollections: [@audios]}"
        "       filter not v_audio.is_deleted and (not has(v_audio, 'type') or v_audio.type == @not_archived_type)"
        "       collect temp = v_audio.chat_id into chat_audios = v_audio"
        "       return chat_audios"
    )

    _mark_chat_audios_as_deleted_query = (
        "for audio in @@audios"
        "   filter audio.chat_id == @chat_id and audio.is_deleted == false"
        "   update {_key: audio._key, is_deleted: true, modified_at : @modified_at, deleted_at: @deleted_at} in @@audios options {ignoreRevs: true}"
    )

    async def create_audio(
        self: ArangoGraphMethods,
        telegram_message: pyrogram.types.Message,
        chat_id: int,
        audio_type: AudioType,
        chat_scores: ChatScores,
    ) -> Optional[Audio]:
        """
        Create Audio alongside necessary vertices and edges in the ArangoDB.

        Parameters
        ----------
        telegram_message : pyrogram.types.Message
            Telegram message to create the Audio from
        chat_id : int
            Chat ID this message belongs to.
        audio_type : AudioType
            Type of the Audio.
        chat_scores : ChatScores
            Scores of the parent chat.

        Returns
        -------
        Audio, optional
            Audio if the creation was successful, otherwise, return None

        Raises
        ------
        EdgeCreationFailed
            If creation of the related edges was unsuccessful.
        """
        if telegram_message is None:
            return None

        try:
            audio, successful = await Audio.insert(Audio.parse(telegram_message, chat_id, audio_type, chat_scores))
        except TelegramMessageWithNoAudio as e:
            # this message doesn't contain any valid audio file
            await self.mark_old_audio_vertices_as_deleted(chat_id, telegram_message.id)
        except Exception as e:
            logger.exception(e)
        else:
            if audio and successful:
                from tase.db.arangodb.graph.edges import HasHashtag

                audio: Audio = audio
                try:
                    hashtags = audio.find_hashtags()
                except ValueError:
                    pass
                else:
                    for hashtag, start_index, mention_source in hashtags:
                        hashtag_vertex = await self.get_or_create_hashtag(hashtag)

                        if hashtag_vertex:
                            has_hashtag = await HasHashtag.get_or_create_edge(
                                audio,
                                hashtag_vertex,
                                mention_source,
                                start_index,
                            )
                            if has_hashtag is None:
                                raise EdgeCreationFailed(HasHashtag.__class__.__name__)
                        else:
                            pass

                chat = await self.get_or_create_chat(telegram_message.chat)
                try:
                    from tase.db.arangodb.graph.edges import SentBy

                    sent_by_edge = await SentBy.get_or_create_edge(audio, chat)
                    if sent_by_edge is None:
                        raise EdgeCreationFailed(SentBy.__class__.__name__)
                except (InvalidFromVertex, InvalidToVertex):
                    pass

                # since checking for audio file validation is done above, there is no need to it again.
                await self._create_file_with_file_ref_edge(telegram_message, audio)

                if audio.is_forwarded:
                    if telegram_message.forward_from:
                        forwarded_from = await self.get_or_create_user(telegram_message.forward_from)
                    elif telegram_message.forward_from_chat:
                        forwarded_from = await self.get_or_create_chat(telegram_message.forward_from_chat)
                    else:
                        forwarded_from = None

                    if forwarded_from is not None:
                        try:
                            from tase.db.arangodb.graph.edges import ForwardedFrom

                            forwarded_from_edge = await ForwardedFrom.get_or_create_edge(audio, forwarded_from)
                            if forwarded_from_edge is None:
                                raise EdgeCreationFailed(ForwardedFrom.__class__.__name__)
                        except (InvalidFromVertex, InvalidToVertex):
                            pass

                    # todo: the `forwarded_from` edge from `audio` to the `original audio` must be checked later

                if audio.via_bot:
                    bot = await self.get_or_create_user(telegram_message.via_bot)
                    try:
                        from tase.db.arangodb.graph.edges import ViaBot

                        via_bot_edge = await ViaBot.get_or_create_edge(audio, bot)
                        if via_bot_edge is None:
                            raise EdgeCreationFailed(ViaBot.__class__.__name__)
                    except (InvalidFromVertex, InvalidToVertex):
                        pass

                return audio

        return None

    async def get_or_create_audio(
        self,
        telegram_message: pyrogram.types.Message,
        chat_id: int,
        audio_type: AudioType,
        chat_scores: ChatScores,
    ) -> Optional[Audio]:
        """
        Get Audio if it exists in ArangoDB, otherwise, create Audio alongside necessary vertices and edges in the
        ArangoDB.

        Parameters
        ----------
        telegram_message : pyrogram.types.Message
            Telegram message to create the Audio from
        chat_id : int
            Chat ID this message belongs to.
        audio_type : AudioType
            Type of the audio.
        chat_scores : ChatScores
            Scores of the parent chat.

        Returns
        -------
        Audio, optional
            Audio if the operation was successful, otherwise, return None

        Raises
        ------
        EdgeCreationFailed
            If creation of the related edges was unsuccessful.
        """
        if telegram_message is None:
            return None

        audio = None

        try:
            audio = await Audio.get(Audio.parse_key(telegram_message, chat_id))
        except TelegramMessageWithNoAudio:
            await self.mark_old_audio_vertices_as_deleted(chat_id, telegram_message.id)
        else:
            if audio is None:
                # audio vertex does not exist in the database, create it.
                audio = await self.create_audio(telegram_message, chat_id, audio_type, chat_scores)

                if audio:
                    await self.mark_old_audio_vertices_as_deleted(
                        chat_id=chat_id,
                        message_id=audio.message_id,
                        excluded_key=audio.key,
                    )

        return audio

    async def update_or_create_audio(
        self: ArangoGraphMethods,
        telegram_message: pyrogram.types.Message,
        chat_id: int,
        audio_type: AudioType,
        chat_scores: ChatScores,
    ) -> Optional[Audio]:
        """
        Update Audio alongside necessary vertices and edges in the ArangoDB if it exists, otherwise, create it.

        Parameters
        ----------
        telegram_message : pyrogram.types.Message
            Telegram message to create the Audio from.
        chat_id : int
            Chat ID this message belongs to.
        audio_type : AudioType
            Type of the audio.
        chat_scores : ChatScores
            Scores of the parent chat.

        Returns
        -------
        Audio, optional
            Audio if the creation was successful, otherwise, return None

        Raises
        ------
        EdgeCreationFailed
            If creation of the related edges was unsuccessful.
        """
        if telegram_message is None:
            return None

        audio = None

        try:
            audio: Optional[Audio] = await Audio.get(Audio.parse_key(telegram_message, chat_id))
        except TelegramMessageWithNoAudio:
            await self.mark_old_audio_vertices_as_deleted(chat_id, telegram_message.id)
        else:
            if audio is not None:
                # the message has not been `deleted`, update remaining attributes
                # the type of the audio after update is not changed. So, the previous type is used for updating the current one.

                # since it is checked for `TelegramMessageWithNoAudio` error earlier, there is no need to do it again.
                if await audio.update(Audio.parse(telegram_message, chat_id, audio.type, chat_scores)):
                    # update connected hashtag vertices and edges
                    await self._update_connected_hashtags(audio)

                    # since checking for audio file validation is done above, there is no need to it again.
                    await self._create_file_with_file_ref_edge(telegram_message, audio)

                    # get older valid audio vertices to process
                    # audio file has been changed, the connected hashtag and file vertices must be updated.
                    await self.mark_old_audio_vertices_as_deleted(
                        chat_id=chat_id,
                        message_id=audio.message_id,
                        excluded_key=audio.key,
                    )
            else:
                # audio vertex does not exist in the database, create it.
                audio = await self.create_audio(telegram_message, chat_id, audio_type, chat_scores)
                if audio:
                    await self.mark_old_audio_vertices_as_deleted(
                        chat_id=chat_id,
                        message_id=audio.message_id,
                        excluded_key=audio.key,
                    )
        return audio

    async def _create_file_with_file_ref_edge(
        self: ArangoGraphMethods,
        telegram_message: pyrogram.types.Message,
        audio: Audio,
    ) -> None:
        """
        Create a `File` vertex and connect it to the given `Audio` vertex with a `FileRef` edge.

        Parameters
        ----------
        telegram_message : pyrogram.types.Message
            Telegram message to use for creating the file vertex and file_ref edge.
        audio : Audio
            `Audio` vertex to create the file and file_ref for.

        Raises
        ------
        EdgeCreationFailed
            If creation of the related edges was unsuccessful.
        """
        file = await self.get_or_create_file(telegram_message)
        try:
            from tase.db.arangodb.graph.edges import FileRef

            file_ref_edge = await FileRef.get_or_create_edge(audio, file)
            if file_ref_edge is None:
                raise EdgeCreationFailed(FileRef.__class__.__name__)

        except (InvalidFromVertex, InvalidToVertex):
            pass

    async def _update_connected_hashtags(
        self: ArangoGraphMethods,
        audio: Audio,
    ) -> None:
        """
        Update connected `hashtag` vertices and edges connected to and `Audio` vertex after being updated.

        Parameters
        ----------
        audio : Audio
            Updated audio vertex.

        Raises
        ------
        EdgeCreationFailed
            If creation of the related edges was unsuccessful.
        """
        from tase.db.arangodb.graph.edges import HasHashtag

        try:
            hashtags = audio.find_hashtags()
        except ValueError:
            pass
        else:
            # get the current hashtag vertices and edges connected to this audio vertex
            current_hashtags_and_edges_list = await self.get_audio_hashtags_with_edges(audio.id)
            current_vertices = {hashtag.key for hashtag, _ in current_hashtags_and_edges_list}
            current_edges = {edge.key for _, edge, in current_hashtags_and_edges_list}

            current_vertices_mapping = {hashtag.key: hashtag for hashtag, _ in current_hashtags_and_edges_list}
            current_edges_mapping = {edge.key: edge for _, edge, in current_hashtags_and_edges_list}

            # find the new hashtag vertices and edges keys
            new_vertices = set()
            new_edges = set()

            new_vertices_mapping = dict()
            new_edges_mapping = dict()

            for hashtag_string, start_index, mention_source in hashtags:
                hashtag_key = Hashtag.parse_key(hashtag_string)
                edge_key = HasHashtag.parse_has_hashtag_key(audio.key, hashtag_key, mention_source, start_index)

                new_vertices.add(hashtag_key)
                new_edges.add(edge_key)

                new_vertices_mapping[hashtag_key] = hashtag_string
                new_edges_mapping[edge_key] = (hashtag_key, start_index, mention_source)

            # find the difference between the current and new state of vertices and edges
            removed_vertices = current_vertices - new_vertices  # since a hashtag vertex might be connected to other audio vertices, it's best not to delete it.
            removed_edges = current_edges - new_edges

            to_create_vertices = new_vertices - current_vertices
            to_create_edges = new_edges - current_edges

            # delete the removed edges
            for edge_key in removed_edges:
                to_be_removed_edge: HasHashtag = current_edges_mapping[edge_key]
                if not await to_be_removed_edge.delete():
                    logger.error(f"Error in deleting `HasHashtag` edge with key `{to_be_removed_edge.key}`")

            # create new hashtag vertices
            for hashtag_key in to_create_vertices:
                hashtag_string: str = new_vertices_mapping.get(hashtag_key, None)
                if hashtag_string:
                    _vertex = await self.get_or_create_hashtag(hashtag_string)
                    if _vertex:
                        current_vertices_mapping[hashtag_key] = _vertex

            # create the new edges
            for edge_key in to_create_edges:
                hashtag_key, start_index, mention_source = new_edges_mapping[edge_key]
                hashtag_vertex = current_vertices_mapping.get(hashtag_key, None)
                if hashtag_vertex:
                    has_hashtag = await HasHashtag.get_or_create_edge(
                        audio,
                        hashtag_vertex,
                        mention_source,
                        start_index,
                    )
                    if has_hashtag is None:
                        raise EdgeCreationFailed(HasHashtag.__class__.__name__)

    async def find_audio_by_download_url(
        self,
        download_url: str,
    ) -> Optional[Audio]:
        """
        Get Audio by `download_url` in the ArangoDB

        Parameters
        ----------
        download_url : str
            Download URL to get the Audio from

        Returns
        -------
        Audio, optional
            Audio if it exists with the given `download_url` parameter, otherwise, return None

        """
        if download_url is None:
            return None

        return await Audio.find_one({"download_url": download_url})

    async def get_audio_from_hit(
        self,
        hit: Hit,
    ) -> Optional[Audio]:
        """
        Get an `Audio` vertex from the given `Hit` vertex

        Parameters
        ----------
        hit : Hit
            Hit to get the audio from.

        Returns
        -------
        Audio, optional
            Audio if operation was successful, otherwise, return None

        Raises
        ------
        ValueError
            If the given `Hit` vertex has more than one linked `Audio` vertices.
        """
        if hit is None:
            return

        from tase.db.arangodb.graph.edges import Has

        res = collections.deque()
        async with await Audio.execute_query(
            self._get_audio_from_hit_query,
            bind_vars={
                "start_vertex": hit.id,
                "audios": Audio.__collection_name__,
                "has": Has.__collection_name__,
            },
        ) as cursor:
            async for doc in cursor:
                res.append(Audio.from_collection(doc))

        if len(res) > 1:
            raise ValueError(f"Hit with id `{hit.id}` have more than one linked audios.")

        if res:
            return res[0]

        return None

    async def is_audio_valid_for_inline_mode(
        self,
        *,
        hit_download_url: str = None,
        audio_vertex_key: str = None,
    ) -> Optional[bool]:
        """
        Check for inline validity of an `Audio` vertex from a `Hit` vertex `download_url`

        Parameters
        ----------
        hit_download_url : str
            Download URL of a hit vertex connected to the audio vertex
        audio_vertex_key : str
            Audio vertex key

        Returns
        -------
        bool, optional
            Whether the audio vertex is valid for inline search if it exists in the database, otherwise return None

        """
        if audio_vertex_key is None and (hit_download_url is None or not len(hit_download_url)):
            return False

        from tase.db.arangodb.graph.edges import Has

        if hit_download_url is not None:
            async with await Audio.execute_query(
                self._check_audio_validity_for_inline_mode_by_hit_download_url,
                bind_vars={
                    "@hits": Hit.__collection_name__,
                    "hit_download_url": hit_download_url,
                    "audios": Audio.__collection_name__,
                    "has": Has.__collection_name__,
                },
            ) as cursor:
                async for doc in cursor:
                    return doc

        else:
            audio: Audio = await Audio.get(audio_vertex_key)
            return audio.valid_for_inline_search if audio is not None else False

        return False

    async def get_audio_from_hit_download_url(
        self,
        hit_download_url: str = None,
    ) -> Optional[Audio]:
        """
        Get the audio vertex connected to a hit vertex with the given download URL.

        Parameters
        ----------
        hit_download_url : str
            Download URL of a hit vertex connected to the audio vertex

        Returns
        -------
        Audio, optional
            Audio vertex connected to the hit vertex with the given download URL.

        """
        if not hit_download_url:
            return None

        from tase.db.arangodb.graph.edges import Has

        async with await Audio.execute_query(
            self._get_audio_by_hit_download_url,
            bind_vars={
                "@hits": Hit.__collection_name__,
                "hit_download_url": hit_download_url,
                "audios": Audio.__collection_name__,
                "has": Has.__collection_name__,
            },
        ) as cursor:
            async for doc in cursor:
                return Audio.from_collection(doc)

        return None

    async def get_user_download_history(
        self,
        user: User,
        filter_by_valid_for_inline_search: bool = True,
        offset: int = 0,
        limit: int = 15,
    ) -> Deque[Audio]:
        """
        Get `User` download history.

        Parameters
        ----------
        user : User
            User to get the download history
        filter_by_valid_for_inline_search : bool, default : True
            Whether to only get audio files that are valid to be shown in inline mode
        offset : int, default : 0
            Offset to get the download history query after
        limit : int, default : 15
            Number of `Audio`s to query

        Returns
        -------
        deque
            Audios that the given user has downloaded

        """
        if user is None:
            return collections.deque()

        from tase.db.arangodb.graph.edges import Has

        res = collections.deque()
        async with await Audio.execute_query(
            self._get_user_download_history_inline_query if filter_by_valid_for_inline_search else self._get_user_download_history_query,
            bind_vars={
                "start_vertex": user.id,
                "has": Has.__collection_name__,
                "audios": Audio.__collection_name__,
                "interactions": Interaction.__collection_name__,
                "interaction_type": InteractionType.DOWNLOAD_AUDIO.value,
                "archived_lst": [AudioType.ARCHIVED.value, AudioType.UPLOADED.value, AudioType.SENT_BY_USERS.value],
                "offset": offset,
                "limit": limit,
            },
        ) as cursor:
            async for doc in cursor:
                res.append(Audio.from_collection(doc))

        return res

    async def get_audios_from_keys(
        self,
        keys: List[str],
    ) -> Deque[Audio]:
        """
        Get a list of Audios from a list of keys.

        Parameters
        ----------
        keys : List[str]
            List of keys to get the audios from.

        Returns
        -------
        Deque
            List of Audios if operation was successful, otherwise, return None

        """
        if not keys:
            return collections.deque()

        res = collections.deque()
        async with await Audio.execute_query(
            self._get_audios_by_keys,
            bind_vars={
                "@audios": Audio.__collection_name__,
                "audio_keys": list(keys),
            },
        ) as cursor:
            async for audios_lst in cursor:
                for doc in audios_lst:
                    res.append(Audio.from_collection(doc))

        return res

    async def remove_audio_from_all_playlists(
        self,
        audio_vertex_id: str,
    ) -> None:
        """
        Remove an `Audio` vertex from all playlists.

        Parameters
        ----------
        audio_vertex_id : str
            ID of the `Audio` vertex.

        """
        if not audio_vertex_id:
            return

        from tase.db.arangodb.graph.vertices import Playlist
        from tase.db.arangodb.graph.edges import Has

        async with await Audio.execute_query(
            self._remove_audio_from_all_playlists_query,
            bind_vars={
                "audio_vertex_id": audio_vertex_id,
                "@has_": Has.__collection_name__,
                "has": Has.__collection_name__,
                "playlists": Playlist.__collection_name__,
            },
        ) as _:
            pass

    async def mark_chat_audios_as_deleted(
        self,
        chat_id: int,
    ) -> None:
        """
        Mark `Audio` vertices belonging to a chat as deleted.

        Parameters
        ----------
        chat_id : int
            ID of the chat to mark the audio vertices as deleted.
        """
        if chat_id is None:
            return

        now = get_now_timestamp()

        async with await Audio.execute_query(
            self._mark_chat_audios_as_deleted_query,
            bind_vars={
                "chat_id": chat_id,
                "@audios": Audio.__collection_name__,
                "modified_at": now,
                "deleted_at": now,
            },
        ) as _:
            pass

    async def get_not_deleted_audio_vertices(
        self,
        chat_id: int,
        message_id: int,
        excluded_key: str,
    ) -> List[Audio]:
        """
        Get `Audio` vertices with the given `chat_id` and `message_id` attributes which are not deleted.

        Parameters
        ----------
        chat_id : int
            ID of the chat the audio vertex belongs to.
        message_id : int
            ID of the telegram message containing this audio file.
        excluded_key : str
            Audio vertex key to exclude from this query.

        Returns
        -------
        list of Audio
            List of `Audio` vertices if operation was successful.

        """
        if chat_id is None or message_id is None:
            return []

        res = collections.deque()
        async with await Audio.execute_query(
            self._get_not_deleted_audios_by_chat_id_and_message_id,
            bind_vars={
                "@audios": Audio.__collection_name__,
                "chat_id": chat_id,
                "message_id": message_id,
                "excluded_key": excluded_key,
            },
        ) as cursor:
            async for doc in cursor:
                res.append(Audio.from_collection(doc))

        return list(res)

    async def mark_old_audio_vertices_as_deleted(
        self,
        chat_id: int,
        message_id: int,
        excluded_key: Optional[str] = None,
    ) -> None:
        """
        Mark `Audio` vertices with the given `chat_id` and `message_id` attributes as deleted.

        This method marks the matching vertices as deleted and removes them from all playlists

        Parameters
        ----------
        chat_id : int
            ID of the chat the audio vertex belongs to.
        message_id : int
            ID of the telegram message containing this audio file.
        excluded_key : str, optional
            Audio vertex key to exclude from this query.

        """
        if chat_id is None or message_id is None:
            return

        deleted_at = get_now_timestamp()

        bind_vars = {
            "@audios": Audio.__collection_name__,
            "chat_id": chat_id,
            "message_id": message_id,
            "not_archived": AudioType.NOT_ARCHIVED.value,
            "deleted_at": deleted_at,
        }
        if excluded_key:
            bind_vars["excluded_key"] = excluded_key

        coroutines = collections.deque()

        async with await Audio.execute_query(
            self._mark_old_audios_as_deleted_by_chat_id_and_message_id_with_excluded_key
            if excluded_key
            else self._mark_old_audios_as_deleted_by_chat_id_and_message_id_without_excluded_key,
            bind_vars=bind_vars,
        ) as cursor:
            async for doc in cursor:
                if "_id" in doc:
                    coroutines.append(self.remove_audio_from_all_playlists(doc["_id"]))

        if coroutines:
            await asyncio.gather(*coroutines)

    async def iter_audios(
        self,
        now: int,
    ) -> Generator[Audio, None, None]:
        if now is None:
            return

        async with await Audio.execute_query(
            self._iter_audios_query,
            bind_vars={
                "@audios": Audio.__collection_name__,
                "now": now,
            },
        ) as cursor:
            async for doc in cursor:
                yield Audio.from_collection(doc)

    async def get_audio_by_key(
        self,
        key: str,
    ) -> Optional[Audio]:
        return await Audio.get(key)

    async def get_new_indexed_audio_files_count(self) -> int:
        """
        Get the total number of indexed audio files in the last 24 hours

        Returns
        -------
        int
            Total number of indexed audio files in the last 24 hours

        """
        checkpoint = get_now_timestamp() - 86400000

        async with await Audio.execute_query(
            self._get_new_indexed_audios_count_query,
            bind_vars={
                "@audios": Audio.__collection_name__,
                "checkpoint": checkpoint,
            },
        ) as cursor:
            async for doc in cursor:
                return int(doc)

        return 0

    async def get_total_indexed_audio_files_count(self) -> int:
        """
        Get the total number of indexed audio files

        Returns
        -------
        int
            Total number of indexed audio files

        """
        async with await Audio.execute_query(
            self._get_total_indexed_audios_count_query,
            bind_vars={
                "@audios": Audio.__collection_name__,
            },
        ) as cursor:
            async for doc in cursor:
                return int(doc)

        return 0

    async def get_not_archived_downloaded_audios(self) -> Deque[Deque[Audio]]:
        """
        Get the downloaded audio vertices that have not been archived yet.

        Returns
        -------
        deque
            A nested deque containing the results grouped by `chat_id` attribute.

        """
        from tase.db.arangodb.graph.edges import Has

        res = collections.deque()
        async with await Audio.execute_query(
            self._get_not_archived_downloaded_audios,
            bind_vars={
                "@interactions": Interaction.__collection_name__,
                "audios": Audio.__collection_name__,
                "has": Has.__collection_name__,
                "now": get_now_timestamp(),
                "interaction_type": InteractionType.DOWNLOAD_AUDIO.value,
                "not_archived_type": AudioType.NOT_ARCHIVED.value,
            },
        ) as cursor:
            async for audio_doc_lst in cursor:
                group = collections.deque()
                group_keys = set()

                if not audio_doc_lst:
                    continue

                for audio_doc in audio_doc_lst:
                    if not audio_doc:
                        continue

                    if audio_doc["_key"] not in group_keys:
                        _audio = Audio.from_collection(audio_doc)
                        group.append(_audio)
                        group_keys.add(_audio.key)

                if group:
                    res.append(group)

        return res
