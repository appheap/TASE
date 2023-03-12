from __future__ import annotations

import collections
import hashlib
from typing import Optional, Deque

import pyrogram
from pydantic import Field

from aioarango.models import PersistentIndex
from tase.my_logger import logger
from .base_document import BaseDocument


class ThumbnailFile(BaseDocument):
    """
    Represents the information about the downloaded thumbnail of an audio file.

    Attributes
    ----------
    thumbnail_file_unique_id : str
        File unique ID of the original thumbnail.
    index : int
        Index of the original thumbnail in the list of thumbnails.
    file_name : str
        Name of the thumbnail file stored on disk.
    file_hash : str
        Hash of the thumbnail file. The hash is calculated using SHA-512 algorithm.
    is_checked : bool, default : False
        Whether this downloaded file is checked or not. In the checking process, the related audio and thumbnail vertices is updated.
    """

    __collection_name__ = "doc_thumbnail_files"
    schema_version = 1
    __indexes__ = [
        PersistentIndex(
            custom_version=1,
            name="thumbnail_file_unique_id",
            fields=[
                "thumbnail_file_unique_id",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="file_hash",
            fields=[
                "file_hash",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="is_checked",
            fields=[
                "is_checked",
            ],
        ),
    ]

    thumbnail_file_unique_id: str
    index: int

    file_name: str
    file_hash: str
    is_checked: bool = Field(default=False)

    @classmethod
    def parse_key(
        cls,
        chat_id: int,
        message_id: int,
        telegram_audio: pyrogram.types.Audio,
        index: int,
    ) -> Optional[str]:
        if chat_id is None or message_id is None or not telegram_audio or index is None:
            return None

        return f"{chat_id}:{message_id}:{telegram_audio.file_unique_id}:{index}"

    @classmethod
    def parse(
        cls,
        chat_id: int,
        message_id: int,
        telegram_audio: pyrogram.types.Audio,
        telegram_thumbnail: pyrogram.types.Thumbnail,
        index: int,
        file_name: str,
    ) -> Optional[ThumbnailFile]:
        if not telegram_thumbnail or not file_name:
            return None

        key = cls.parse_key(chat_id, message_id, telegram_audio, index)
        if not key:
            return None

        with open(f"downloads/{file_name}.jpg", "rb") as opened_file:
            hex_digest = hashlib.sha512(opened_file.read()).hexdigest()

            return ThumbnailFile(
                key=key,
                thumbnail_file_unique_id=telegram_thumbnail.file_unique_id,
                index=index,
                file_name=file_name,
                file_hash=hex_digest,
            )

    async def mark_as_checked(self) -> bool:
        self_copy = self.copy(deep=True)
        self_copy.is_checked = True
        return await self.update(
            self_copy,
            reserve_non_updatable_fields=False,
            check_for_revisions_match=False,
        )


class ThumbnailFileMethods:
    _get_unchecked_thumbnail_files = (
        "for doc in @@thumbnail_docs" "   filter doc.is_checked == false" "   sort doc.created_at asc" "   limit @skip, @size" "   return doc"
    )

    async def get_unchecked_thumbnail_files(
        self,
        from_: int = 0,
        size: int = 500,
    ) -> Deque[ThumbnailFile]:
        """
        Get unchecked thumbnail files that need to be uploaded.

        Parameters
        ----------
        from_ : int, default : 0
            Number of items to skip.
        size : int, default : 500
            Number of items to get.

        Returns
        -------
        Deque of ThumbnailFile
            A deque of unchecked thumbnail files.

        """
        res = collections.deque()
        async with await ThumbnailFile.execute_query(
            self._get_unchecked_thumbnail_files,
            bind_vars={
                "@thumbnail_docs": ThumbnailFile.__collection_name__,
                "skip": from_,
                "size": size,
            },
            stream=True,
        ) as cursor:
            async for doc in cursor:
                res.append(ThumbnailFile.from_collection(doc))

        return res

    async def get_thumbnail_file_document(
        self,
        chat_id: int,
        message_id: int,
        telegram_audio: pyrogram.types.Audio,
        index: int,
    ) -> Optional[ThumbnailFile]:
        return await ThumbnailFile.get(
            ThumbnailFile.parse_key(
                chat_id=chat_id,
                message_id=message_id,
                telegram_audio=telegram_audio,
                index=index,
            )
        )

    async def get_thumbnail_file_document_by_key(self, key: str) -> Optional[ThumbnailFile]:
        if not key:
            return None

        return await ThumbnailFile.get(key)

    async def get_thumbnail_file_document_by_file_hash(self, file_hash: str) -> Optional[ThumbnailFile]:
        if not file_hash:
            return None

        return await ThumbnailFile.find_one(
            filters={
                "file_hash": file_hash,
            }
        )

    async def create_thumbnail_file_document(
        self,
        chat_id: int,
        message_id: int,
        telegram_audio: pyrogram.types.Audio,
        telegram_thumbnail: pyrogram.types.Thumbnail,
        index: int,
        file_name: str,
    ) -> Optional[ThumbnailFile]:
        """
        Create a thumbnail from the given arguments.

        Parameters
        ----------
        chat_id : int
            ID of the chat the thumbnail was downloaded from.
        message_id : int
            ID of the message this thumbnail belongs to.
        telegram_audio : pyrogram.types.Audio
            Telegram audio file this thumbnail belongs to.
        telegram_thumbnail : pyrogram.types.Thumbnail
            Telegram thumbnail object to create the `ThumbnailFile` object from.
        index : int
            Index of the original thumbnail in the list of thumbnails.
        file_name : str
            Name of the downloaded file.


        Returns
        -------
        ThumbnailFile, optional
            Created ThumbnailFile document if the operation was successful, otherwise return `None`.
        """
        if chat_id is None or message_id is None or not telegram_audio or not telegram_thumbnail or index is None or not file_name:
            return None

        try:
            thumbnail, successful = await ThumbnailFile.insert(
                ThumbnailFile.parse(
                    chat_id=chat_id,
                    message_id=message_id,
                    telegram_audio=telegram_audio,
                    telegram_thumbnail=telegram_thumbnail,
                    index=index,
                    file_name=file_name,
                )
            )
        except Exception as e:
            logger.exception(e)
        else:
            if thumbnail and successful:
                return thumbnail

        return None

    async def get_or_create_thumbnail_file_document(
        self,
        chat_id: int,
        message_id: int,
        telegram_audio: pyrogram.types.Audio,
        telegram_thumbnail: pyrogram.types.Thumbnail,
        index: int,
        file_name: str,
    ) -> Optional[ThumbnailFile]:
        """
        Get a thumbnail from the given arguments if it exists in the database, otherwise create it.

        Parameters
        ----------
        chat_id : int
            ID of the chat the thumbnail was downloaded from.
        message_id : int
            ID of the message this thumbnail belongs to.
        telegram_audio : pyrogram.types.Audio
            Telegram audio file this thumbnail belongs to.
        telegram_thumbnail : pyrogram.types.Thumbnail
            Telegram thumbnail object to create the `ThumbnailFile` object from.
        index : int
            Index of the original thumbnail in the list of thumbnails.
        file_name : str
            Name of the downloaded file.

        Returns
        -------
        ThumbnailFile, optional
            ThumbnailFile document if the operation was successful, otherwise return `None`.
        """
        thumbnail = await ThumbnailFile.get(
            ThumbnailFile.parse_key(
                chat_id=chat_id,
                message_id=message_id,
                telegram_audio=telegram_audio,
                index=index,
            )
        )
        if not thumbnail:
            thumbnail = await self.create_thumbnail_file_document(
                chat_id=chat_id,
                message_id=message_id,
                telegram_audio=telegram_audio,
                telegram_thumbnail=telegram_thumbnail,
                index=index,
                file_name=file_name,
            )

        return thumbnail
