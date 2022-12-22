from __future__ import annotations

import copy
from typing import Optional, Tuple, Deque

import pyrogram
from elastic_transport import ObjectApiResponse
from pydantic import Field

from tase.common.preprocessing import clean_text, empty_to_null
from tase.common.utils import datetime_to_timestamp, async_timed, get_now_timestamp
from tase.db.arangodb import graph as graph_models
from tase.errors import TelegramMessageWithNoAudio
from tase.my_logger import logger
from .base_document import BaseDocument
from ...arangodb.enums import TelegramAudioType, InteractionType, HitType, AudioType
from ...arangodb.helpers import (
    ElasticQueryMetadata,
    BitRateType,
    InteractionCount,
    HitCount,
)
from ...db_utils import (
    get_telegram_message_media_type,
    parse_audio_key,
    is_audio_valid_for_inline,
    parse_audio_document_key_from_raw_attributes,
)


class Audio(BaseDocument):
    schema_version = 1

    __index_name__ = "audios_index"
    __mappings__ = {
        "properties": {
            "schema_version": {"type": "integer"},
            "created_at": {"type": "long"},
            "modified_at": {"type": "long"},
            "chat_id": {"type": "long"},
            "message_id": {"type": "long"},
            "message_caption": {"type": "text"},
            "raw_message_caption": {"type": "keyword"},
            "message_date": {"type": "date"},
            "file_unique_id": {"type": "keyword"},
            "duration": {"type": "integer"},
            "performer": {"type": "text"},
            "raw_performer": {"type": "keyword"},
            "title": {"type": "text"},
            "raw_title": {"type": "keyword"},
            "file_name": {"type": "text"},
            "raw_file_name": {"type": "keyword"},
            "mime_type": {"type": "keyword"},
            "file_size": {"type": "integer"},
            "date": {"type": "date"},
            "views": {"type": "long"},
            "downloads": {"type": "long"},
            "shares": {"type": "long"},
            "search_hits": {"type": "long"},
            "non_search_hits": {"type": "long"},
            "likes": {"type": "long"},
            "dislikes": {"type": "long"},
            "audio_type": {"type": "integer"},
            "valid_for_inline_search": {"type": "boolean"},
            "type": {"type": "integer"},
            "archive_chat_id": {"type": "long"},
            "archive_message_id": {"type": "long"},
            "estimated_bit_rate_type": {"type": "integer"},
            "is_forwarded": {"type": "boolean"},
            "is_deleted": {"type": "boolean"},
            "deleted_at": {"type": "long"},
            "is_edited": {"type": "boolean"},
        }
    }

    __non_updatable_fields__ = (
        "views",
        "downloads",
        "shares",
        "search_hits",
        "non_search_hits",
        "likes",
        "dislikes",
        "deleted_at",
        "archive_chat_id",
        "archive_message_id",
    )
    __search_fields__ = [
        "performer",
        "title",
        "file_name",
        "message_caption",
    ]

    chat_id: int
    message_id: int
    message_caption: Optional[str]
    raw_message_caption: Optional[str]
    message_date: int

    file_unique_id: str
    duration: Optional[int]
    performer: Optional[str]
    raw_performer: Optional[str]
    title: Optional[str]
    raw_title: Optional[str]
    file_name: Optional[str]
    raw_file_name: Optional[str]
    mime_type: Optional[str]
    file_size: int
    date: int

    views: int = Field(default=0)
    downloads: int = Field(default=0)
    shares: int = Field(default=0)
    search_hits: int = Field(default=0)
    non_search_hits: int = Field(default=0)
    likes: int = Field(default=0)
    dislikes: int = Field(default=0)
    audio_type: TelegramAudioType  # whether the audio file is shown in the `audios` or `files/documents` section of telegram app
    valid_for_inline_search: bool
    """
     when an audio's title is None or the audio is shown in document section of
     telegram, then that audio could not be shown in telegram inline mode. Moreover, it should not have keyboard
     markups like `add_to_playlist`, etc... . On top of that, if any audio of this kind gets downloaded through
     query search, then, it cannot be shown in `download_history` section or any other sections that work in inline
     mode.
    """
    type: AudioType
    archive_chat_id: Optional[int]
    archive_message_id: Optional[int]

    estimated_bit_rate_type: BitRateType
    is_forwarded: bool
    is_deleted: bool
    deleted_at: Optional[int]  # this is not always accurate
    is_edited: bool

    @classmethod
    def parse_id(
        cls,
        telegram_message: pyrogram.types.Message,
        chat_id: int,
    ) -> Optional[str]:
        """
        Parse the `ID` from the given `telegram_message` argument if it contains a valid audio file, otherwise raise
        an `ValueError` exception.

        Parameters
        ----------
        telegram_message : pyrogram.types.Message
            Telegram message to parse the ID from
        chat_id : int
            Chat ID this message belongs to.

        Returns
        -------
        str, optional
            Parsed ID if the parsing was successful, otherwise return `None` if the `telegram_message` is `None`.

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

        _id = cls.parse_id(telegram_message, chat_id)
        if _id is None:
            return None

        audio, telegram_audio_type = get_telegram_message_media_type(telegram_message)
        if telegram_audio_type == TelegramAudioType.NON_AUDIO:
            raise TelegramMessageWithNoAudio(telegram_message.id, telegram_message.chat.id)

        title = getattr(audio, "title", None)

        valid_for_inline = is_audio_valid_for_inline(audio, telegram_audio_type)

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
            id=_id,
            chat_id=telegram_message.chat.id,
            message_id=telegram_message.id,
            message_caption=caption,
            raw_message_caption=raw_caption,
            message_date=datetime_to_timestamp(telegram_message.date),
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
            ########################################
            views=telegram_message.views or 0,
            valid_for_inline_search=valid_for_inline,
            estimated_bit_rate_type=BitRateType.estimate(
                audio.file_size,
                duration,
            ),
            audio_type=telegram_audio_type,
            type=audio_type,
            is_forwarded=True if telegram_message.forward_date else False,
            is_deleted=True if telegram_message.empty else False,
            is_edited=True if telegram_message.edit_date else False,
        )

    @classmethod
    def parse_from_audio_vertex(cls, audio_vertex: graph_models.vertices.Audio) -> Optional[Audio]:
        """
        Parse the `Audio` document from an `Audio` vertex object.

        Parameters
        ----------
        audio_vertex : graph_models.vertices.Audio
            Audio vertex to parse the audio document from.

        Returns
        -------
        Audio, optional
            Parsed audio document if operation was successful.

        """
        if not audio_vertex or not audio_vertex.key:
            return None

        return Audio(
            id=audio_vertex.key,
            created_at=audio_vertex.created_at,
            modified_at=audio_vertex.modified_at,
            schema_version=audio_vertex.schema_version,  # todo: is this correct?
            chat_id=audio_vertex.chat_id,
            message_id=audio_vertex.message_id,
            message_caption=audio_vertex.message_caption,
            raw_message_caption=audio_vertex.raw_message_caption,
            message_date=audio_vertex.message_date,
            file_unique_id=audio_vertex.file_unique_id,
            duration=audio_vertex.duration,
            performer=audio_vertex.performer,
            raw_performer=audio_vertex.raw_performer,
            title=audio_vertex.title,
            raw_title=audio_vertex.raw_title,
            file_name=audio_vertex.file_name,
            raw_file_name=audio_vertex.raw_file_name,
            mime_type=audio_vertex.mime_type,
            file_size=audio_vertex.file_size,
            date=audio_vertex.date,
            views=audio_vertex.views,
            audio_type=audio_vertex.audio_type,
            valid_for_inline_search=audio_vertex.valid_for_inline_search,
            type=audio_vertex.type,
            archive_chat_id=audio_vertex.archive_chat_id,
            archive_message_id=audio_vertex.archive_message_id,
            estimated_bit_rate_type=audio_vertex.estimated_bit_rate_type,
            is_forwarded=audio_vertex.is_forwarded,
            is_deleted=audio_vertex.is_deleted,
            deleted_at=audio_vertex.deleted_at,
            is_edited=audio_vertex.is_edited,
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
            retry_on_conflict=True,
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
            retry_on_conflict=True,
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
            retry_on_conflict=True,
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

    @classmethod
    async def search_by_download_url(
        cls,
        download_url: str,
    ) -> Optional[Audio]:
        if download_url is None:
            return None
        db_docs = []

        try:
            res: ObjectApiResponse = await cls.__es__.search(
                index=cls.__index_name__,
                query={
                    "match": {
                        "download_url": download_url,
                    },
                },
            )

            hits = res.body["hits"]["hits"]

            for index, hit in enumerate(hits, start=1):
                try:
                    db_doc = cls.from_index(hit=hit, rank=len(hits) - index + 1)
                except ValueError:
                    # happens when `hit` is None
                    pass
                else:
                    db_docs.append(db_doc)

        except Exception as e:
            logger.exception(e)

        return db_docs[0] if len(db_docs) else None

    @classmethod
    def get_query(
        cls,
        query: Optional[str],
        filter_by_valid_for_inline_search: Optional[bool] = True,
    ) -> Optional[dict]:
        if filter_by_valid_for_inline_search:
            return {
                "bool": {
                    "must": {
                        "multi_match": {
                            "query": query,
                            "fuzziness": "AUTO",
                            "type": "best_fields",
                            "minimum_should_match": "75%",
                            "fields": cls.__search_fields__,
                        }
                    },
                    "must_not": [
                        {"term": {"audio_type": {"value": TelegramAudioType.NON_AUDIO.value}}},
                    ],
                    "filter": [
                        {"term": {"is_deleted": False}},
                        {"term": {"valid_for_inline_search": True}},
                    ],
                }
            }
        else:
            return {
                "bool": {
                    "must": {
                        "multi_match": {
                            "query": query,
                            "fuzziness": "AUTO",
                            "type": "best_fields",
                            "minimum_should_match": "75%",
                            "fields": cls.__search_fields__,
                        }
                    },
                    "must_not": [
                        {"term": {"audio_type": {"value": TelegramAudioType.NON_AUDIO.value}}},
                    ],
                    "filter": [
                        {"term": {"is_deleted": False}},
                    ],
                }
            }

    @classmethod
    def get_sort(
        cls,
    ) -> Optional[dict]:
        return {
            "_score": {"order": "desc"},
            "estimated_bit_rate_type": {"order": "desc"},
            "date": {"order": "desc"},
            "downloads": {"order": "desc"},
            "shares": {"order": "desc"},
            "search_hits": {"order": "desc"},
            "non_search_hits": {"order": "desc"},
            "likes": {"order": "desc"},
            "dislikes": {"order": "asc"},
        }

    async def update_by_interaction_count(
        self,
        interaction_count: InteractionCount,
    ) -> bool:
        """
        Update the attributes of the `Audio` index with the given `InteractionCount` object

        Parameters
        ----------
        interaction_count : InteractionCount
            InteractionCount object to update the index document with

        Returns
        -------
        bool
            Whether the update was successful or not

        """
        if interaction_count is None:
            return False

        self_copy: Audio = self.copy(deep=True)
        if interaction_count.interaction_type == InteractionType.DOWNLOAD:
            self_copy.downloads += interaction_count.count
        elif interaction_count.interaction_type == InteractionType.SHARE:
            self_copy.shares += interaction_count.count
        elif interaction_count.interaction_type == InteractionType.LIKE:
            if interaction_count.is_active:
                self_copy.likes += interaction_count.count
            else:
                if self_copy.likes > 0:
                    self_copy.likes -= interaction_count.count
        elif interaction_count.interaction_type == InteractionType.DISLIKE:
            if interaction_count.is_active:
                self_copy.dislikes += interaction_count.count
            else:
                if self_copy.dislikes > 0:
                    self_copy.dislikes -= interaction_count.count

        return await self.update(
            self_copy,
            reserve_non_updatable_fields=False,
            retry_on_failure=True,
            retry_on_conflict=True,
        )

    async def update_by_hit_count(
        self,
        hit_count: HitCount,
    ) -> bool:
        """
        Update the attributes of the `Audio` index with the given `HitCount` object

        Parameters
        ----------
        hit_count : HitCount
            HitCount object to update the index document with

        Returns
        -------
        bool
            Whether the update was successful or not

        """
        if hit_count is None:
            return False

        self_copy: Audio = self.copy(deep=True)
        if hit_count.hit_type in (HitType.SEARCH, HitType.INLINE_SEARCH):
            self_copy.search_hits += hit_count.count
        elif hit_count.hit_type == HitType.INLINE_COMMAND:
            self_copy.non_search_hits += hit_count.count

        return await self.update(
            self_copy,
            reserve_non_updatable_fields=False,
            retry_on_failure=True,
            retry_on_conflict=True,
        )


class AudioMethods:
    async def create_audio(
        self,
        telegram_message: pyrogram.types.Message,
        chat_id: int,
        audio_type: AudioType,
    ) -> Optional[Audio]:
        """
        Create Audio document in the ElasticSearch.

        Parameters
        ----------
        telegram_message : pyrogram.types.Message
            Telegram message to create the Audio from.
        chat_id : int
            Chat ID this message belongs to.
        audio_type : AudioType
            Type of the audio.

        Returns
        -------
        Audio, optional
            Audio if the creation was successful, otherwise, return None

        """
        try:
            audio, successful = await Audio.create(Audio.parse(telegram_message, chat_id, audio_type))
        except TelegramMessageWithNoAudio:
            # this message doesn't contain any valid audio file
            await self.mark_old_audios_as_deleted(
                chat_id=chat_id,
                message_id=telegram_message.id,
            )
        else:
            if audio and successful:
                return audio

        return None

    async def get_or_create_audio(
        self,
        telegram_message: pyrogram.types.Message,
        chat_id: int,
        audio_type: AudioType,
    ) -> Optional[Audio]:
        """
        Get Audio if it exists in ElasticSearch, otherwise, create Audio document.

        Parameters
        ----------
        telegram_message : pyrogram.types.Message
            Telegram message to create the Audio from.
        chat_id : int
            Chat ID this message belongs to.
        audio_type : AudioType
            Type of the audio.

        Returns
        -------
        Audio, optional
            Audio if the operation was successful, otherwise, return None

        """
        if telegram_message is None or chat_id is None:
            return None

        audio = None

        try:
            audio = await Audio.get(Audio.parse_id(telegram_message, chat_id))
        except TelegramMessageWithNoAudio:
            await self.mark_old_audios_as_deleted(
                chat_id=chat_id,
                message_id=telegram_message.id,
            )
        else:
            if audio is None:
                # audio does not exist in the index, create it
                audio = await self.create_audio(telegram_message, chat_id, audio_type)

                if audio:
                    await self.mark_old_audios_as_deleted(
                        chat_id=chat_id,
                        message_id=telegram_message.id,
                        excluded_id=audio.id,
                    )

        return audio

    async def update_or_create_audio(
        self: AudioMethods,
        telegram_message: pyrogram.types.Message,
        chat_id: int,
        audio_type: AudioType,
    ) -> Optional[Audio]:
        """
        Update Audio document in the ElasticSearch if it exists, otherwise, create it.

        Parameters
        ----------
        telegram_message : pyrogram.types.Message
            Telegram message to create the Audio from.
        chat_id : int
            Chat ID this message belongs to.
        audio_type : AudioType
            Type of the audio.

        Returns
        -------
        Audio, optional
            Audio if the creation was successful, otherwise, return None

        """
        if telegram_message is None or chat_id is None:
            return None

        audio = None

        try:
            audio: Optional[Audio] = await Audio.get(Audio.parse_id(telegram_message, chat_id))
        except TelegramMessageWithNoAudio:
            await self.mark_old_audios_as_deleted(
                chat_id=chat_id,
                message_id=telegram_message.id,
            )
        else:
            if audio is None:
                # audio does not exist in the index, create it
                audio = await self.create_audio(telegram_message, chat_id, audio_type)
                if audio:
                    await self.mark_old_audios_as_deleted(
                        chat_id=chat_id,
                        message_id=telegram_message.id,
                        excluded_id=audio.id,
                    )
            else:
                # the type of the audio after update is not changed. So, the previous type is used for updating the current one.
                if await audio.update(Audio.parse(telegram_message, chat_id, audio.type)):
                    # get older valid audio docs to process
                    await self.mark_old_audios_as_deleted(
                        chat_id=chat_id,
                        message_id=audio.message_id,
                        excluded_id=audio.id,
                    )

        return audio

    async def get_audio_by_id(
        self,
        id: str,
    ) -> Optional[Audio]:
        """
        Get `Audio` by its `ID`

        Parameters
        ----------
        id : str
            ID of the `Audio` to get

        Returns
        -------
        Audio, optional
            Audio if it exists in ElasticSearch, otherwise, return None

        """
        return await Audio.get(id)

    @async_timed()
    async def search_audio(
        self,
        query: str,
        from_: int = 0,
        size: int = 10,
        filter_by_valid_for_inline_search: Optional[bool] = True,
    ) -> Tuple[Optional[Deque[Audio]], Optional[ElasticQueryMetadata]]:
        """
        Search among the audio files with the given query

        Parameters
        ----------
        query : str
            Query string to search for
        from_ : int, default : 0
            Number of audio files to skip in the query
        size : int, default : 50
            Number of audio files to return
        filter_by_valid_for_inline_search : bool, default: True
            Whether to filter audios by the validity to be shown in inline search of telegram


        Returns
        -------
        tuple
            List of audio files matching the query alongside the query metadata

        """
        if query is None or not len(query) or from_ is None or size is None:
            return None, None

        audios, query_metadata = await Audio.search(
            query,
            from_,
            size,
            filter_by_valid_for_inline_search,
        )
        return audios, query_metadata

    async def mark_old_audios_as_deleted(
        self,
        chat_id: int,
        message_id: int,
        excluded_id: Optional[str] = None,
    ) -> None:
        """
        Mark `Audio` documents with the given `chat_id` and `message_id` attributes which as deleted.

        Parameters
        ----------
        chat_id : int
            ID of the chat the audio document belongs to.
        message_id : int
            ID of the telegram message containing this audio file.
        excluded_id : str, optional
            Audio document ID to exclude from this query.

        """
        if chat_id is None or message_id is None:
            return

        deleted_at = get_now_timestamp()

        try:
            await Audio.__es__.update_by_query(
                index=Audio.__index_name__,
                conflicts="proceed",
                query={
                    "bool": {
                        "must_not": {"ids": {"values": [excluded_id]}},
                        "filter": [
                            {"term": {"is_deleted": {"value": False}}},
                            {"term": {"chat_id": {"value": chat_id}}},
                            {"term": {"message_id": {"value": message_id}}},
                        ],
                    }
                    if excluded_id
                    else {
                        "filter": [
                            {"term": {"is_deleted": {"value": False}}},
                            {"term": {"chat_id": {"value": chat_id}}},
                            {"term": {"message_id": {"value": message_id}}},
                        ],
                    }
                },
                script={
                    "source": f"ctx._source.is_deleted = true; ctx._source.deleted_at = params.deleted_at; ctx._source.modified_at = params.deleted_at",
                    "lang": "painless",
                    "params": {
                        "deleted_at": deleted_at,
                    },
                },
            )

        except Exception as e:
            logger.exception(e)

    async def mark_chat_audios_as_deleted(
        self,
        chat_id: int,
    ) -> None:
        """
        Mark `Audio` documents with the given `chat_id` as deleted.

        Parameters
        ----------
        chat_id : int
            ID of the chat the audio documents belongs to.

        """
        if chat_id is None:
            return

        deleted_at = get_now_timestamp()

        try:
            await Audio.__es__.update_by_query(
                index=Audio.__index_name__,
                conflicts="proceed",
                query={
                    "bool": {
                        "filter": [
                            {"term": {"is_deleted": {"value": False}}},
                            {"term": {"chat_id": {"value": chat_id}}},
                        ],
                    }
                },
                script={
                    "source": f"ctx._source.is_deleted = true; ctx._source.deleted_at = params.deleted_at; ctx._source.modified_at = params.deleted_at",
                    "lang": "painless",
                    "params": {
                        "deleted_at": deleted_at,
                    },
                },
            )

        except Exception as e:
            logger.exception(e)
