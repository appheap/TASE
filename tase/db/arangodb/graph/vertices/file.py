from typing import Optional

import pyrogram

from .base_vertex import BaseVertex


class File(BaseVertex):
    _collection_name = "files"
    schema_version = 1

    file_unique_id: str

    @classmethod
    def parse_key(
        cls,
        telegram_message: pyrogram.types.Message,
    ) -> Optional[str]:
        if telegram_message is None:
            return None

        if telegram_message.audio:
            _audio = telegram_message.audio
        elif telegram_message.document:
            _audio = telegram_message.document
        else:
            raise ValueError("Unexpected value for `message`: nor audio nor document")

        return _audio.file_unique_id

    @classmethod
    def parse(
        cls,
        telegram_message: pyrogram.types.Message,
    ) -> Optional["File"]:
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
        ValueError
            If `telegram_message` argument does not contain any valid audio file.
        """
        key = File.parse_key(telegram_message)
        if key is None:
            return None

        if telegram_message is None:
            return None

        if telegram_message.audio:
            _audio = telegram_message.audio
        elif telegram_message.document:
            _audio = telegram_message.document
        else:
            raise ValueError("Unexpected value for `message`: nor audio nor document")

        return File(
            key=key,
            file_unique_id=_audio.file_unique_id,
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

        Raises
        ------
        ValueError
            If `telegram_message` argument does not contain any valid audio file.
        """
        if telegram_message is None:
            return None

        file, successful = File.insert(File.parse(telegram_message))
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

        file = File.get(File.parse_key(telegram_message))
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

        Raises
        ------
        ValueError
            If `telegram_message` argument does not contain any valid audio file.
        """
        if telegram_message is None:
            return None

        file = File.get(File.parse_key(telegram_message))
        if file is None:
            return self.create_file(telegram_message)
        else:
            successful = file.update(File.parse(telegram_message))
            if successful:
                return file
            else:
                return None
