from __future__ import annotations

from typing import Union, Optional

import pyrogram

from .base_document import BaseDocument
from ..enums import TelegramAudioType
from ... import elasticsearchdb
from ...db_utils import get_telegram_message_media_type


class Audio(BaseDocument):
    _collection_name = "doc_audios"
    schema_version = 1

    chat_id: int
    message_id: int

    file_id: str
    file_unique_id: str

    @classmethod
    def parse_key(
        cls,
        input_arg: Union[pyrogram.types.Message, elasticsearchdb.Audio],
        telegram_client_id: int,
    ) -> Optional[str]:
        """
        Parse the `key` from the given `telegram_message` argument if it contains a valid audio file, otherwise raise
        an `ValueError` exception.

        Parameters
        ----------
        input_arg : pyrogram.types.Message or elasticsearch_models.Audio
            Telegram message to parse the key from or `Audio` document from elasticsearchDB

        telegram_client_id : int
            ID of the telegram client who got this message

        Returns
        -------
        str, optional
            Parsed key if the parsing was successful, otherwise return `None` if the `telegram_message` is `None`.

        Raises
        ------
        ValueError
            If `input_arg` parameter is `pyrogram.types.Message` instance and does not contain any valid audio file,
            or when is not an instance of either of `pyrogram.types.Message` or `elastic_models.Audio`
        """
        if isinstance(input_arg, pyrogram.types.Message):
            audio, audio_type = get_telegram_message_media_type(input_arg)
            if audio is None or audio_type == TelegramAudioType.NON_AUDIO:
                raise ValueError("Unexpected value for `message`: nor audio nor document")

            return f"{str(telegram_client_id)}:{audio.file_unique_id}:{input_arg.chat.id}:{input_arg.id}"

        elif isinstance(input_arg, elasticsearchdb.Audio):
            audio = input_arg
            return f"{str(telegram_client_id)}:{audio.file_unique_id}:{audio.chat_id}:{audio.message_id}"
        else:
            # this not a valid instance
            raise ValueError("This is not valid instance")

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
        ValueError
            If `telegram_message` parameter does not contain any valid audio file.
        """
        if telegram_message is None:
            return None

        # do not catch `ValueError` exception from the following line
        key = Audio.parse_key(telegram_message, telegram_client_id)

        if key is None:
            return None

        audio, audio_type = get_telegram_message_media_type(telegram_message)
        if audio is None or audio_type == TelegramAudioType.NON_AUDIO:
            raise ValueError("Unexpected value for `message`: nor audio nor document")

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

        try:
            audio = Audio.get(Audio.parse_key(telegram_message, telegram_client_id))
        except ValueError:
            audio = None
        else:
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
                updated = audio.update(Audio.parse(telegram_message, telegram_client_id))

        return audio
