from __future__ import annotations

from typing import Optional

import pyrogram

from tase.errors import TelegramMessageWithNoAudio
from .base_document import BaseDocument
from ..base.index import PersistentIndex
from ..enums import TelegramAudioType
from ...db_utils import get_telegram_message_media_type


class Audio(BaseDocument):
    _collection_name = "doc_audios"
    schema_version = 1
    _extra_indexes = [
        PersistentIndex(
            version=1,
            name="file_id",
            fields=[
                "file_id",
            ],
        ),
        PersistentIndex(
            version=1,
            name="file_unique_id",
            fields=[
                "file_unique_id",
            ],
        ),
        PersistentIndex(
            version=1,
            name="chat_id",
            fields=[
                "chat_id",
            ],
        ),
        PersistentIndex(
            version=1,
            name="message_id",
            fields=[
                "message_id",
            ],
        ),
    ]

    chat_id: int
    message_id: int

    file_id: str
    file_unique_id: str

    @classmethod
    def parse_key(
        cls,
        telegram_message: pyrogram.types.Message,
        telegram_client_id: int,
    ) -> Optional[str]:
        """
        Parse the `key` from the given `telegram_message` argument if it contains a valid audio file, otherwise raise
        an `ValueError` exception.

        Parameters
        ----------
        telegram_message : pyrogram.types.Message
            Telegram message to parse the key from or `Audio` document from elasticsearchDB

        telegram_client_id : int
            ID of the telegram client who got this message

        Returns
        -------
        str, optional
            Parsed key if the parsing was successful, otherwise return `None` if the `telegram_message` is `None`.

        """

        return f"{telegram_client_id}:{telegram_message.chat.id}:{telegram_message.id}"

    @classmethod
    def parse(
        cls,
        telegram_message: pyrogram.types.Message,
        telegram_client_id: int,
    ) -> Optional[Audio]:
        """
        Parse an `Audio` from the given `telegram_message` argument.

        Parameters
        ----------
        telegram_message : pyrogram.types.Message
            Telegram message to parse the `Audio` from

        telegram_client_id : int
            ID of the telegram client who got this message

        Returns
        -------
        Audio, optional
            Parsed `Audio` if parsing was successful, otherwise, return `None`.

        Raises
        ------
        TelegramMessageWithNoAudio
            If `telegram_message` parameter does not contain any valid audio file.
        """
        if telegram_message is None:
            return None

        key = Audio.parse_key(telegram_message, telegram_client_id)

        if key is None:
            return None

        audio, audio_type = get_telegram_message_media_type(telegram_message)
        if audio is None or audio_type == TelegramAudioType.NON_AUDIO:
            raise TelegramMessageWithNoAudio(telegram_message.id, telegram_message.chat.id)

        return Audio(
            key=key,
            chat_id=telegram_message.chat.id,
            message_id=telegram_message.id,
            file_id=audio.file_id,
            file_unique_id=audio.file_unique_id,
        )


class AudioMethods:
    def create_audio(
        self,
        telegram_message: pyrogram.types.Message,
        telegram_client_id: int,
    ) -> Optional[Audio]:
        """
        Create Audio document in the ArangoDB.

        Parameters
        ----------
        telegram_message : pyrogram.types.Message
            Telegram message to create the Audio from

        telegram_client_id : int
            ID of the telegram client who got this message

        Returns
        -------
        Audio, optional
            Audio if the creation was successful, otherwise, return None

        Raises
        ------
        Exception
            If creation of the related vertices or edges was unsuccessful.
        """
        if telegram_message is None:
            return None

        try:
            audio, successful = Audio.insert(Audio.parse(telegram_message, telegram_client_id))
        except ValueError:
            # the message does not contain any valid audio file
            pass
        else:
            if audio and successful:
                return audio

        return None

    def get_or_create_audio(
        self,
        telegram_message: pyrogram.types.Message,
        telegram_client_id: int,
    ) -> Optional[Audio]:
        """
        Get Audio document if it exists in ArangoDB, otherwise, create Audio document in the ArangoDB.

        Parameters
        ----------
        telegram_message : pyrogram.types.Message
            Telegram message to create the Audio from

        telegram_client_id : int
            ID of the telegram client who got this message

        Returns
        -------
        Audio, optional
            Audio if the operation was successful, otherwise, return None

        """
        if telegram_message is None:
            return None

        audio = Audio.get(Audio.parse_key(telegram_message, telegram_client_id))
        if audio is None:
            audio = self.create_audio(telegram_message, telegram_client_id)

        return audio

    def update_or_create_audio(
        self,
        telegram_message: pyrogram.types.Message,
        telegram_client_id: int,
    ) -> Optional[Audio]:
        """
        Update `Audio` document if it exists in ArangoDB, otherwise, create the document in the ArangoDB.

        Parameters
        ----------
        telegram_message : pyrogram.types.Message
            Telegram message to create the Audio from

        telegram_client_id : int
            ID of the telegram client who got this message

        Returns
        -------
        Audio, optional
            Audio if the operation was successful, otherwise, return None

        """
        if telegram_message is None:
            return None

        try:
            audio = Audio.get(Audio.parse_key(telegram_message, telegram_client_id))
        except ValueError:
            audio = None
        else:
            if audio is None:
                audio = self.create_audio(telegram_message, telegram_client_id)
            else:
                try:
                    updated = audio.update(Audio.parse(telegram_message, telegram_client_id))
                except ValueError:
                    updated = False

        return audio

    def get_audio_by_key(
        self,
        telegram_client_id: int,
        audio_key: str,
    ) -> Optional[Audio]:
        """
        Get `Audio` by its `key` from given arguments

        Parameters
        ----------
        telegram_client_id : int
            ID of the telegram client
        audio_key : str
            Key of the `Audio` vertex or index (from arangodb or elasticsearch)

        Returns
        -------
        Audio, optional
            Audio if it exists in the ArangoDB, otherwise, return None

        """
        if telegram_client_id is None or audio_key is None:
            return None

        return Audio.get(f"{telegram_client_id}:{audio_key}")

    def has_audio_by_key(
        self,
        telegram_client_id: int,
        audio_key: str,
    ) -> bool:
        """
        Check whether an `Audio` exists in the ArangoDB

        Parameters
        ----------
        telegram_client_id : int
            ID of the telegram client
        audio_key : str
            Key of the `Audio` vertex or index (from arangodb or elasticsearch)

        Returns
        -------
        Audio, optional
            Audio if it exists in the ArangoDB, otherwise, return None

        """
        if telegram_client_id is None or audio_key is None:
            return False

        return Audio.has(f"{telegram_client_id}:{audio_key}")
