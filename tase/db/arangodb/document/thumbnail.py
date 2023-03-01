from __future__ import annotations

from typing import Optional

import pyrogram

from aioarango.models import PersistentIndex
from tase.my_logger import logger
from .base_document import BaseDocument
from ...db_utils import parse_thumbnail_document_key


class Thumbnail(BaseDocument):
    __collection_name__ = "doc_thumbnails"
    schema_version = 1
    __indexes__ = [
        PersistentIndex(
            custom_version=1,
            name="telegram_client_id",
            fields=[
                "telegram_client_id",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="thumbnail_file_unique_id",
            fields=[
                "thumbnail_file_unique_id",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="photo_file_unique_id",
            fields=[
                "photo_file_unique_id",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="photo_file_id",
            fields=[
                "photo_file_id",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="archive_chat_id",
            fields=[
                "archive_chat_id",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="archive_message_id",
            fields=[
                "archive_message_id",
            ],
        ),
    ]

    telegram_client_id: int

    thumbnail_file_unique_id: str
    photo_file_unique_id: str
    photo_file_id: str

    # These attributes show the uploaded photo message information.
    archive_chat_id: int
    archive_message_id: int

    @classmethod
    def parse_key(
        cls,
        telegram_client_id: int,
        telegram_uploaded_photo_message: pyrogram.types.Message,
    ) -> Optional[str]:
        if telegram_client_id is None or not telegram_uploaded_photo_message:
            return None

        return parse_thumbnail_document_key(
            telegram_client_id,
            telegram_uploaded_photo_message.chat.id,
            telegram_uploaded_photo_message.id,
        )

    @classmethod
    def parse(
        cls,
        telegram_client_id: int,
        telegram_thumbnail: pyrogram.types.Thumbnail,
        telegram_uploaded_photo_message: pyrogram.types.Message,
    ) -> Optional[Thumbnail]:
        if telegram_client_id is None or not telegram_thumbnail or not telegram_uploaded_photo_message or not telegram_uploaded_photo_message.photo:
            return None

        photo = telegram_uploaded_photo_message.photo

        key = cls.parse_key(telegram_client_id, telegram_uploaded_photo_message)
        if not key:
            return None

        return Thumbnail(
            key=key,
            telegram_client_id=telegram_client_id,
            photo_file_unique_id=photo.file_unique_id,
            thumbnail_file_unique_id=telegram_thumbnail.file_unique_id,
            photo_file_id=photo.file_id,
            archive_chat_id=telegram_uploaded_photo_message.chat.id,
            archive_message_id=telegram_uploaded_photo_message.id,
        )


class ThumbnailMethods:
    async def get_thumbnail_doc_by_archive_message_info(
        self,
        telegram_client_id: int,
        archive_chat_id: int,
        archive_message_id: int,
    ) -> Optional[Thumbnail]:
        return await Thumbnail.find_one(
            filters={
                "telegram_client_id": telegram_client_id,
                "archive_chat_id": archive_chat_id,
                "archive_message_id": archive_message_id,
            }
        )

    async def create_thumbnail_document(
        self,
        telegram_client_id: int,
        telegram_thumbnail: pyrogram.types.Thumbnail,
        telegram_uploaded_photo_message: pyrogram.types.Message,
    ) -> Optional[Thumbnail]:
        """
        Create a thumbnail from the given arguments.

        Parameters
        ----------
        telegram_client_id : int
            ID of the telegram client uploading this thumbnail.
        telegram_thumbnail : pyrogram.types.Thumbnail
            Telegram thumbnail object to use for creating the thumbnail object.
        telegram_uploaded_photo_message : pyrogram.types.Message
            Telegram message to use for creating the thumbnail object.

        Returns
        -------
        Thumbnail, optional
            Created Thumbnail document if the operation was successful, otherwise return `None`.
        """
        try:
            thumbnail, successful = await Thumbnail.insert(
                Thumbnail.parse(
                    telegram_client_id=telegram_client_id,
                    telegram_thumbnail=telegram_thumbnail,
                    telegram_uploaded_photo_message=telegram_uploaded_photo_message,
                )
            )
        except Exception as e:
            logger.exception(e)
        else:
            if thumbnail and successful:
                return thumbnail

        return None

    async def get_or_create_thumbnail_document(
        self,
        telegram_client_id: int,
        telegram_thumbnail: pyrogram.types.Thumbnail,
        telegram_uploaded_photo_message: pyrogram.types.Message,
    ) -> Optional[Thumbnail]:
        """
        Get a thumbnail from the given arguments if it exists in the database, otherwise create it.

        Parameters
        ----------
        telegram_client_id : int
            ID of the telegram client uploading this thumbnail.
        telegram_thumbnail : pyrogram.types.Thumbnail
            Telegram thumbnail object to use for creating or getting the thumbnail object.
        telegram_uploaded_photo_message : pyrogram.types.Message
            Telegram message to use for creating or getting the thumbnail object.

        Returns
        -------
        Thumbnail, optional
            Thumbnail document if the operation was successful, otherwise return `None`.
        """
        thumbnail = await Thumbnail.get(Thumbnail.parse_key(telegram_client_id, telegram_uploaded_photo_message))
        if not thumbnail:
            thumbnail = await self.create_thumbnail_document(
                telegram_client_id=telegram_client_id,
                telegram_thumbnail=telegram_thumbnail,
                telegram_uploaded_photo_message=telegram_uploaded_photo_message,
            )

        return thumbnail
