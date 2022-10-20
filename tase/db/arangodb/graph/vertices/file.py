from __future__ import annotations

from typing import Optional

import pyrogram

from tase.db.db_utils import get_telegram_message_media_type
from tase.errors import TelegramMessageWithNoAudio
from tase.my_logger import logger
from .base_vertex import BaseVertex
from ...enums import TelegramAudioType


class File(BaseVertex):
    _collection_name = "files"
    schema_version = 1

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
    def create_file(
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
            file, successful = File.insert(File.parse(telegram_message))
        except TelegramMessageWithNoAudio:
            pass
        except Exception as e:
            logger.exception(e)
        else:
            if file and successful:
                return file

        return None

    def get_or_create_file(
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
            file = File.get(File.parse_key(telegram_message))
        except TelegramMessageWithNoAudio:
            pass
        except Exception as e:
            logger.exception(e)
        else:
            if file is None:
                file = self.create_file(telegram_message)

        return file

    def update_or_create_file(
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
            file = File.get(File.parse_key(telegram_message))
            if file is None:
                return self.create_file(telegram_message)
            else:
                successful = file.update(File.parse(telegram_message))
                if successful:
                    return file
                else:
                    return None
        except TelegramMessageWithNoAudio:
            pass
        except Exception as e:
            logger.exception(e)

        return None
