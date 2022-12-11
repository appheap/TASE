from __future__ import annotations

from typing import Optional, Tuple, TYPE_CHECKING

import pyrogram

from aioarango.models import PersistentIndex
from tase.db.db_utils import get_telegram_message_media_type
from tase.errors import TelegramMessageWithNoAudio
from tase.my_logger import logger
from .base_vertex import BaseVertex
from ...enums import TelegramAudioType

if TYPE_CHECKING:
    from ..edges import FileRef


class File(BaseVertex):
    _collection_name = "files"
    schema_version = 1
    _extra_indexes = [
        PersistentIndex(
            custom_version=1,
            name="file_unique_id",
            fields=[
                "file_unique_id",
            ],
            unique=True,
        ),
    ]

    file_unique_id: str

    @classmethod
    def parse_key(
        cls,
        telegram_message: pyrogram.types.Message,
    ) -> Optional[str]:
        """
        Parse the key from telegram message

        Parameters
        ----------
        telegram_message : pyrogram.types.Message
            Telegram Message to parse the key from

        Returns
        -------
        str, optional
            Parsed key if successful, otherwise, return None

        Raises
        ------
        TelegramMessageWithNoAudio
            If `telegram_message` argument does not contain any valid audio file.

        """
        if telegram_message is None:
            return None

        audio, audio_type = get_telegram_message_media_type(telegram_message)
        if audio is None or audio_type == TelegramAudioType.NON_AUDIO:
            raise TelegramMessageWithNoAudio(telegram_message.id, telegram_message.chat.id)

        return audio.file_unique_id

    @classmethod
    def parse(
        cls,
        telegram_message: pyrogram.types.Message,
    ) -> Optional[File]:
        """
        Parse an `file` from the given `telegram_message` argument.

        Parameters
        ----------
        telegram_message : pyrogram.types.Message
            Telegram message to parse the `File` from

        Returns
        -------
        File, optional
            Parsed `File` if parsing was successful, otherwise, return `None`.

        Raises
        ------
        TelegramMessageWithNoAudio
            If `telegram_message` argument does not contain any valid audio file.
        """

        if telegram_message is None:
            return None

        key = File.parse_key(telegram_message)
        if key is None:
            return None

        return File(
            key=key,
            file_unique_id=key,
        )


class FileMethods:
    _get_audio_file_with_edge_query = (
        "for v, e in 1..1 outbound @audio_vertex graph @graph_name options {order: 'dfs', edgeCollections: [@file_ref], vertexCollections: [@files]}"
        "   return {vertex: v, edge: e}"
    )

    async def create_file(
        self,
        telegram_message: pyrogram.types.Message,
    ) -> Optional[File]:
        """
        Create a `File` vertex in the ArangoDB.

        Parameters
        ----------
        telegram_message : pyrogram.types.Message
            Telegram message to create the File from

        Returns
        -------
        File, optional
            File vertex if the creation was successful, otherwise, return None.

        """
        if telegram_message is None:
            return None

        try:
            file, successful = await File.insert(File.parse(telegram_message))
        except TelegramMessageWithNoAudio:
            pass
        except Exception as e:
            logger.exception(e)
        else:
            if file and successful:
                return file

        return None

    async def get_or_create_file(
        self,
        telegram_message: pyrogram.types.Message,
    ) -> Optional[File]:
        """
        Get `File` vertex if it exists in the ArangoDB, otherwise, create it.

        Parameters
        ----------
        telegram_message : pyrogram.types.Message
            Telegram message to create the File from

        Returns
        -------
        File, optional
            File vertex if the operation was successful, otherwise, return None.

        Raises
        ------
        ValueError
            If `telegram_message` argument does not contain any valid audio file.
        """
        if telegram_message is None:
            return None

        file = None

        try:
            file = await File.get(File.parse_key(telegram_message))
        except TelegramMessageWithNoAudio:
            pass
        except Exception as e:
            logger.exception(e)
        else:
            if file is None:
                file = await self.create_file(telegram_message)

        return file

    async def update_or_create_file(
        self,
        telegram_message: pyrogram.types.Message,
    ) -> Optional[File]:
        """
        Update `File` vertex if it exists in the ArangoDB, otherwise, create it.

        Parameters
        ----------
        telegram_message : pyrogram.types.Message
            Telegram message to create/update the File from

        Returns
        -------
        File, optional
            File vertex if the operation was successful, otherwise, return None.

        """
        if telegram_message is None:
            return None

        try:
            file = await File.get(File.parse_key(telegram_message))
            if file is None:
                return await self.create_file(telegram_message)
            else:
                successful = await file.update(File.parse(telegram_message))
                if successful:
                    return file
                else:
                    return None
        except TelegramMessageWithNoAudio:
            pass
        except Exception as e:
            logger.exception(e)

        return None

    async def get_audio_file_with_file_ref_edge(
        self,
        audio_vertex_id: str,
    ) -> Tuple[Optional[File], Optional[FileRef]]:
        """
        Get `File` vertex belonging to an `audio` vertex along with the `FileRef` edge.

        Parameters
        ----------
        audio_vertex_id : str
            ID of the audio vertex.

        Returns
        -------
        tuple, optional
            Tuple of `File` vertex and `FileRef` edge.
        """
        if not audio_vertex_id:
            return None, None

        from ..edges import FileRef

        async with await File.execute_query(
            self._get_audio_file_with_edge_query,
            bind_vars={
                "audio_vertex": audio_vertex_id,
                "file_ref": FileRef._collection_name,
                "files": File._collection_name,
            },
        ) as cursor:
            async for d in cursor:
                if "vertex" in d and "edge" in d:
                    return File.from_collection(d["vertex"]), FileRef.from_collection(d["edge"])

        return None, None
