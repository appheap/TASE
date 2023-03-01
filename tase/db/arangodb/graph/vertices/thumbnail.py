from __future__ import annotations

from typing import Optional

import pyrogram.types

from aioarango.models import PersistentIndex
from tase.common.utils import datetime_to_timestamp
from tase.my_logger import logger
from .base_vertex import BaseVertex


class Thumbnail(BaseVertex):
    """
    Represents the information about the thumbnail of an audio file.

    Attributes
    ----------
    photo_file_unique_id : str
        File unique ID of the uploaded photo.
    thumbnail_file_unique_id : str
        File unique ID of the original thumbnail.
    width : int
        Width of the original thumbnail and the uploaded photo.
    height : int
        Height of the original thumbnail and the uploaded photo.
    file_size : int
        Size of the original thumbnail file or the uploaded photo.
    date : int
        Timestamp in which the photo was uploaded. (in nanoseconds)
    archive_chat_id : int
        ID of the chat where the photo was uploaded.
    archive_message_id : int
        ID of the message which the photo belongs to.
    """

    schema_version = 1
    __collection_name__ = "thumbnails"
    __indexes__ = [
        PersistentIndex(
            custom_version=1,
            name="photo_file_unique_id",
            fields=[
                "photo_file_unique_id",
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
    __non_updatable_fields__ = []

    photo_file_unique_id: str
    thumbnail_file_unique_id: str

    # These attributes are the same for both the thumbnail and the uploaded photo.
    width: int
    height: int
    file_size: int

    # This attribute is for the uploaded photo
    date: int

    # These attributes show the uploaded photo message information.
    archive_chat_id: int
    archive_message_id: int

    @classmethod
    def parse_key(
        cls,
        telegram_thumbnail: pyrogram.types.Thumbnail,
    ) -> Optional[str]:
        if not telegram_thumbnail:
            return None

        return telegram_thumbnail.file_unique_id

    @classmethod
    def parse(
        cls,
        telegram_thumbnail: pyrogram.types.Thumbnail,
        telegram_uploaded_photo_message: pyrogram.types.Message,
    ) -> Optional[Thumbnail]:
        if not telegram_thumbnail or not telegram_uploaded_photo_message or not telegram_uploaded_photo_message.photo:
            return None

        photo = telegram_uploaded_photo_message.photo

        key = cls.parse_key(telegram_thumbnail)
        if not key:
            return None

        return Thumbnail(
            key=key,
            photo_file_unique_id=photo.file_unique_id,
            thumbnail_file_unique_id=telegram_thumbnail.file_unique_id,
            width=photo.width,
            height=photo.height,
            file_size=photo.file_size,
            date=datetime_to_timestamp(photo.date),
            archive_chat_id=telegram_uploaded_photo_message.chat.id,
            archive_message_id=telegram_uploaded_photo_message.id,
        )


class ThumbnailMethods:
    async def get_thumbnail(self, telegram_thumbnail: pyrogram.types.Thumbnail) -> Optional[Thumbnail]:
        return await Thumbnail.get(Thumbnail.parse_key(telegram_thumbnail))

    async def get_thumbnail_by_archive_message_info(
        self,
        archive_chat_id: int,
        archive_message_id: int,
    ) -> Optional[Thumbnail]:
        return await Thumbnail.find_one(
            filters={
                "archive_chat_id": archive_chat_id,
                "archive_message_id": archive_message_id,
            }
        )

    async def create_thumbnail(
        self,
        telegram_thumbnail: pyrogram.types.Thumbnail,
        telegram_uploaded_photo_message: pyrogram.types.Message,
    ) -> Optional[Thumbnail]:
        try:
            thumbnail, successful = await Thumbnail.insert(
                Thumbnail.parse(
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

    async def get_or_create_thumbnail(
        self,
        telegram_thumbnail: pyrogram.types.Thumbnail,
        telegram_uploaded_photo_message: pyrogram.types.Message,
    ) -> Optional[Thumbnail]:
        thumbnail = await Thumbnail.get(Thumbnail.parse_key(telegram_thumbnail))
        if not thumbnail:
            thumbnail = await self.create_thumbnail(
                telegram_thumbnail=telegram_thumbnail,
                telegram_uploaded_photo_message=telegram_uploaded_photo_message,
            )

        return thumbnail
