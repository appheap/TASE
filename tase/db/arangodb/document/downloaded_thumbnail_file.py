from __future__ import annotations

import collections
import hashlib
from typing import Optional, Deque

import pyrogram
from pydantic import Field

from aioarango.models import PersistentIndex
from tase.my_logger import logger
from .base_document import BaseDocument


class DownloadedThumbnailFile(BaseDocument):
    """
    Represents the information about the downloaded thumbnail of an audio file.

    Attributes
    ----------
    thumbnail_file_unique_id : str
        File unique ID of the original thumbnail.
    index : int
        Index of the original thumbnail in the list of thumbnails.
    chat_id : int
        ID of the chat this thumbnail was downloaded from.
    message_id : int
        ID of the message this thumbnail was downloaded from.
    file_name : str
        Name of the thumbnail file stored on disk.
    file_hash : str
        Hash of the thumbnail file. The hash is calculated using SHA-512 algorithm.
    is_checked : bool, default : False
        Whether this downloaded file is checked or not. In the checking process, the related audio and thumbnail vertices is updated.
    """

    __collection_name__ = "doc_downloaded_thumbnail_files"
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

    chat_id: int
    message_id: int

    file_name: str
    file_hash: str
    is_checked: bool = Field(default=False)

    @classmethod
    def parse_key(
        cls,
        thumbnail_file_unique_id: str,
    ) -> Optional[str]:
        if not thumbnail_file_unique_id:
            return None

        return thumbnail_file_unique_id

    @classmethod
    def parse(
        cls,
        chat_id: int,
        message_id: int,
        telegram_audio: pyrogram.types.Audio,
        telegram_thumbnail: pyrogram.types.Thumbnail,
        index: int,
        file_name: str,
    ) -> Optional[DownloadedThumbnailFile]:
        if not telegram_thumbnail or not file_name:
            return None

        key = cls.parse_key(telegram_thumbnail.file_unique_id)
        if not key:
            return None

        with open(f"downloads/{file_name}.jpg", "rb") as opened_file:
            hex_digest = hashlib.sha512(opened_file.read()).hexdigest()

            return DownloadedThumbnailFile(
                key=key,
                thumbnail_file_unique_id=telegram_thumbnail.file_unique_id,
                index=index,
                chat_id=chat_id,
                message_id=message_id,
                file_name=file_name,
                file_hash=hex_digest,
            )

    async def mark_as_checked(self) -> bool:
        """
        Mark the object as checked. It is done after the file is successfully uploaded to telegram.

        Returns
        -------
        bool
            Whether the update was successful or not.

        """
        self_copy = self.copy(deep=True)
        self_copy.is_checked = True
        return await self.update(
            self_copy,
            reserve_non_updatable_fields=False,
            check_for_revisions_match=False,
        )


class DownloadedThumbnailFileMethods:
    _get_unchecked_thumbnail_files = (
        "for doc in @@thumbnail_docs" "   filter doc.is_checked == false" "   sort doc.created_at asc" "   limit @skip, @size" "   return doc"
    )

    async def get_unchecked_thumbnail_files(
        self,
        from_: int = 0,
        size: int = 500,
    ) -> Deque[DownloadedThumbnailFile]:
        """
        Get unchecked downloaded thumbnail files that need to be uploaded.

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
        async with await DownloadedThumbnailFile.execute_query(
            self._get_unchecked_thumbnail_files,
            bind_vars={
                "@thumbnail_docs": DownloadedThumbnailFile.__collection_name__,
                "skip": from_,
                "size": size,
            },
            stream=True,
        ) as cursor:
            async for doc in cursor:
                res.append(DownloadedThumbnailFile.from_collection(doc))

        return res

    async def get_downloaded_thumbnail_file(self, thumbnail_file_unique_id: str) -> Optional[DownloadedThumbnailFile]:
        """
        Get a `DownloadedThumbnailFile` document by the given parameters.

        Parameters
        ----------
        thumbnail_file_unique_id : str
            File unique ID of the telegram thumbnail object.

        Returns
        -------
        DownloadedThumbnailFile, optional
            `DownloadedThumbnailFile` document is returned if it was found on the database, otherwise `None` is returned.
        """
        return await DownloadedThumbnailFile.get(DownloadedThumbnailFile.parse_key(thumbnail_file_unique_id))

    async def get_downloaded_thumbnail_file_by_key(self, key: str) -> Optional[DownloadedThumbnailFile]:
        """
        Get a `DownloadedThumbnailFile` document by its `key`.

        Parameters
        ----------
        key : str
            Key string to use for getting the object.

        Returns
        -------
        DownloadedThumbnailFile, optional
            `DownloadedThumbnailFile` document is returned if it was found on the database, otherwise `None` is returned.
        """
        if not key:
            return None

        return await DownloadedThumbnailFile.get(key)

    async def get_downloaded_thumbnail_file_by_file_hash(self, file_hash: str) -> Optional[DownloadedThumbnailFile]:
        """
        Get a `DownloadedThumbnailFile` document by its `file_hash`.

        Parameters
        ----------
        file_hash : str
            File hash to use for getting the `DownloadedThumbnailFile` document.

        Returns
        -------
        DownloadedThumbnailFile, optional
            `DownloadedThumbnailFile` with the given `file_hash` is returned if it was found on the database, otherwise `None` is returned.
        """
        if not file_hash:
            return None

        return await DownloadedThumbnailFile.find_one(
            filters={
                "file_hash": file_hash,
            }
        )

    async def create_downloaded_thumbnail_file_document(
        self,
        chat_id: int,
        message_id: int,
        telegram_audio: pyrogram.types.Audio,
        telegram_thumbnail: pyrogram.types.Thumbnail,
        index: int,
        file_name: str,
    ) -> Optional[DownloadedThumbnailFile]:
        """
        Create a downloaded thumbnail file document from the given arguments.

        Parameters
        ----------
        chat_id : int
            ID of the chat the thumbnail was downloaded from.
        message_id : int
            ID of the message this thumbnail belongs to.
        telegram_audio : pyrogram.types.Audio
            Telegram audio file this thumbnail belongs to.
        telegram_thumbnail : pyrogram.types.Thumbnail
            Telegram thumbnail object to create the `DownloadedThumbnailFile` object from.
        index : int
            Index of the original thumbnail in the list of thumbnails.
        file_name : str
            Name of the downloaded file.


        Returns
        -------
        DownloadedThumbnailFile, optional
            Created `DownloadedThumbnailFile` document if the operation was successful, otherwise return `None`.
        """
        if chat_id is None or message_id is None or not telegram_audio or not telegram_thumbnail or index is None or not file_name:
            return None

        try:
            thumbnail, successful = await DownloadedThumbnailFile.insert(
                DownloadedThumbnailFile.parse(
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

    async def get_or_create_downloaded_thumbnail_file(
        self,
        chat_id: int,
        message_id: int,
        telegram_audio: pyrogram.types.Audio,
        telegram_thumbnail: pyrogram.types.Thumbnail,
        index: int,
        file_name: str,
    ) -> Optional[DownloadedThumbnailFile]:
        """
        Get a downloaded thumbnail file from the given arguments if it exists in the database, otherwise create it.

        Parameters
        ----------
        chat_id : int
            ID of the chat the thumbnail was downloaded from.
        message_id : int
            ID of the message this thumbnail belongs to.
        telegram_audio : pyrogram.types.Audio
            Telegram audio file this thumbnail belongs to.
        telegram_thumbnail : pyrogram.types.Thumbnail
            Telegram thumbnail object to create the `DownloadedThumbnailFile` object from.
        index : int
            Index of the original thumbnail in the list of thumbnails.
        file_name : str
            Name of the downloaded file.

        Returns
        -------
        DownloadedThumbnailFile, optional
            DownloadedThumbnailFile document if the operation was successful, otherwise return `None`.
        """
        thumbnail = await DownloadedThumbnailFile.get(DownloadedThumbnailFile.parse_key(telegram_thumbnail.file_unique_id))
        if not thumbnail:
            thumbnail = await self.create_downloaded_thumbnail_file_document(
                chat_id=chat_id,
                message_id=message_id,
                telegram_audio=telegram_audio,
                telegram_thumbnail=telegram_thumbnail,
                index=index,
                file_name=file_name,
            )

        return thumbnail
