from typing import Optional

import pyrogram

from tase.utils import get_timestamp
from .base_vertex import BaseVertex


class Audio(BaseVertex):
    _vertex_name = "audios"

    _do_not_update = [
        "created_at",
        "download_url",
    ]

    chat_id: int
    message_id: int
    message_caption: Optional[str]
    message_date: int

    # file_id: str # todo: is it necessary?
    file_unique_id: str
    duration: Optional[int]
    performer: Optional[str]
    title: Optional[str]
    file_name: Optional[str]
    mime_type: Optional[str]
    file_size: int
    date: int

    download_url: Optional[str]
    is_audio_file: bool  # whether the audio file is shown in the `audios` or `files/documents` section of telegram app
    valid_for_inline_search: bool
    """
     when an audio's title is None or the audio is shown in document section of
     telegram, then that audio could not be shown in telegram inline mode. Moreover, it should not have keyboard
     markups like `add_to_playlist`, etc... . On top of that, if any audio of this kind gets downloaded through
     query search, then, it cannot be shown in `download_history` section or any other sections that work in inline
     mode.
    """

    @staticmethod
    def get_key(
        message: "pyrogram.types.Message",
    ):
        if message.audio:
            _audio = message.audio
        elif message.document:
            _audio = message.document
        else:
            raise ValueError("Unexpected value for `message`: nor audio nor document")
        return f"{_audio.file_unique_id}:{message.chat.id}:{message.id}"

    @staticmethod
    def parse_from_message(
        message: "pyrogram.types.Message",
        old_download_url: str = None,
    ) -> Optional["Audio"]:
        if not message or (message.audio is None and message.document is None):
            return None

        key = Audio.get_key(message)

        if message.audio:
            _audio = message.audio
            is_audio_file = True
        elif message.document:
            _audio = message.document
            is_audio_file = False
        else:
            raise ValueError("Unexpected value for `message`: nor audio nor document")

        title = getattr(_audio, "title", None)

        # todo: check if the following statement is actually true
        valid_for_inline = True if title is not None and is_audio_file is not None else False

        return Audio(
            key=key,
            chat_id=message.chat.id,
            message_id=message.id,
            message_caption=message.caption,
            message_date=get_timestamp(message.date),
            file_unique_id=_audio.file_unique_id,
            duration=getattr(_audio, "duration", None),
            performer=getattr(_audio, "performer", None),
            title=title,
            file_name=_audio.file_name,
            mime_type=_audio.mime_type,
            file_size=_audio.file_size,
            date=get_timestamp(_audio.date),
            download_url=Audio.generate_token_urlsafe() if old_download_url is None else None,
            valid_for_inline_search=valid_for_inline,
            is_audio_file=is_audio_file,
        )

    @classmethod
    def find_by_download_url(
        cls,
        download_url: str,
    ) -> Optional["Audio"]:
        if download_url is None:
            return None

        cursor = cls._db.find({"download_url": download_url})
        if cursor and len(cursor):
            return cls.parse_from_graph(cursor.pop())
        else:
            return None
