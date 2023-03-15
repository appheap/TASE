from __future__ import annotations

from typing import Optional

import pyrogram

from aioarango.models import PersistentIndex
from tase.common.utils import datetime_to_timestamp
from tase.my_logger import logger
from .base_vertex import BaseVertex


class ThumbnailFile(BaseVertex):
    """
    Represents the information about the uploaded thumbnail of an audio file.

    Attributes
    ----------
    photo_file_unique_id : str
        File unique ID of the uploaded photo.
    date : int
        Timestamp in which the photo was uploaded. (in nanoseconds)
    archive_chat_id : int
        ID of the chat where the photo was uploaded.
    archive_message_id : int
        ID of the message which the photo belongs to.
    file_hash : str
        Hash of the thumbnail file. The hash is calculated using SHA-512 algorithm.
    """

    __collection_name__ = "thumbnail_files"
    schema_version = 1
    __indexes__ = [
        PersistentIndex(
            custom_version=1,
            name="file_hash",
            fields=[
                "file_hash",
            ],
            unique=True,
        ),
    ]

    photo_file_unique_id: str
    date: int
    archive_chat_id: int
    archive_message_id: int
    file_hash: str

    @classmethod
    def parse_key(
        cls,
        file_hash: str,
    ) -> Optional[str]:
        if not file_hash:
            return None

        return file_hash

    @classmethod
    def parse(
        cls,
        file_hash: str,
        telegram_uploaded_photo_message: pyrogram.types.Message,
    ) -> Optional[ThumbnailFile]:
        key = cls.parse_key(file_hash)
        if not key:
            return None

        return ThumbnailFile(
            key=key,
            photo_file_unique_id=telegram_uploaded_photo_message.photo.file_unique_id,
            date=datetime_to_timestamp(telegram_uploaded_photo_message.date),
            archive_message_id=telegram_uploaded_photo_message.id,
            archive_chat_id=telegram_uploaded_photo_message.chat.id,
            file_hash=file_hash,
        )


class ThumbnailFileMethods:
    _get_thumbnail_files_of_an_thumbnail_vertex_query = (
        "for thumbnail_v in @@thumbnails"
        "   filter thumbnail_v.file_unique_id == @thumbnail_file_unique_id"
        "   for thumb_file_v in 1..1 outbound thumbnail_v graph @graph_name options {order: 'dfs', edgeCollections: [@has], vertexCollections: [@thumbnail_files]}"
        "       return distinct thumb_file_v"
    )

    async def get_thumbnail_file_by_file_hash(self, file_hash: str) -> Optional[ThumbnailFile]:
        """
        Get a `ThumbnailFile` vertex by its `file_hash`.

        Parameters
        ----------
        file_hash : str
            File hash to use for getting the `ThumbnailFile` vertex.

        Returns
        -------
        ThumbnailFile, optional
            `ThumbnailFile` with the given `file_hash` is returned if it was found on the database, otherwise `None` is returned.
        """
        if not file_hash:
            return None

        return await ThumbnailFile.get(file_hash)

    async def get_thumbnail_file_by_thumbnail_file_unique_id(self, thumbnail_file_unique_id: str) -> Optional[ThumbnailFile]:
        """
        Get the `ThumbnailFile` vertex that belong to a `Thumbnail` vertex with the given `file_unique_id` parameter.

        Parameters
        ----------
        thumbnail_file_unique_id : str
            File unique iD of the thumbnail vertex in query.

        Returns
        -------
        ThumbnailFile
            A `ThumbnailFile` vertex is returned on success.
        """
        if not thumbnail_file_unique_id:
            return None

        from tase.db.arangodb.graph.vertices import Thumbnail, ThumbnailFile
        from tase.db.arangodb.graph.edges import Has

        async with await ThumbnailFile.execute_query(
            self._get_thumbnail_files_of_an_thumbnail_vertex_query,
            bind_vars={
                "@thumbnails": Thumbnail.__collection_name__,
                "thumbnail_file_unique_id": thumbnail_file_unique_id,
                "has": Has.__collection_name__,
                "thumbnail_files": ThumbnailFile.__collection_name__,
            },
        ) as cursor:
            async for doc in cursor:
                obj = ThumbnailFile.from_collection(doc)
                return obj

        return None

    async def create_thumbnail_file(
        self,
        telegram_uploaded_photo_message: pyrogram.types.Message,
        file_hash: str,
    ) -> Optional[ThumbnailFile]:
        """
        Create a thumbnail file from the given arguments.

        Parameters
        ----------
        telegram_uploaded_photo_message : pyrogram.types.Message
            Uploaded photo message to use for creating the `ThumbnailFile` vertex.
        file_hash : str
            Hash of the thumbnail file.

        Returns
        -------
        ThumbnailFile, optional
            Created ThumbnailFile vertex if the operation was successful, otherwise return `None`.
        """
        if not telegram_uploaded_photo_message or not file_hash:
            return None

        try:
            thumbnail, successful = await ThumbnailFile.insert(
                ThumbnailFile.parse(
                    telegram_uploaded_photo_message=telegram_uploaded_photo_message,
                    file_hash=file_hash,
                )
            )
        except Exception as e:
            logger.exception(e)
        else:
            if thumbnail and successful:
                return thumbnail

        return None

    async def get_or_create_thumbnail_file(
        self,
        telegram_uploaded_photo_message: pyrogram.types.Message,
        file_hash: str,
    ) -> Optional[ThumbnailFile]:
        """
        Get a `ThumbnailFile` vertex from the given arguments if it exists in the database, otherwise create it.

        Parameters
        ----------
        telegram_uploaded_photo_message: pyrogram.types.Message
            Uploaded photo message to use for creating the `ThumbnailFile` vertex.
        file_hash : str
            Hash of the thumbnail file.


        Returns
        -------
        ThumbnailFile, optional
            `ThumbnailFile` vertex if the operation was successful, otherwise return `None`.
        """
        thumbnail = await ThumbnailFile.get(ThumbnailFile.parse_key(file_hash=file_hash))
        if not thumbnail:
            thumbnail = await self.create_thumbnail_file(
                telegram_uploaded_photo_message=telegram_uploaded_photo_message,
                file_hash=file_hash,
            )

        return thumbnail
