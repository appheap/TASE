from typing import Optional, List

import pyrogram

from tase.utils import get_timestamp, generate_token_urlsafe
from .base_vertex import BaseVertex


class Audio(BaseVertex):
    _collection_name = "audios"
    schema_version = 1

    _extra_do_not_update_fields = [
        "has_checked_forwarded_message_at",
        "download_url",
        "deleted_at",
    ]

    chat_id: int
    message_id: int
    message_caption: Optional[str]
    message_date: Optional[int]
    message_edit_date: Optional[int]
    views: Optional[int]
    reactions: Optional[List[str]]
    forward_date: Optional[int]
    forward_from_chat_id: Optional[int]
    forward_from_message_id: Optional[int]
    forward_signature: Optional[str]
    forward_sender_name: Optional[str]
    via_bot: bool
    has_protected_content: Optional[bool]
    # forward_from_chat : forward_from => Chat
    # forward_from : forward_from => Chat
    # via_bot : via_bot => User

    # file_id: str # todo: is it necessary?
    file_unique_id: str
    duration: Optional[int]
    performer: Optional[str]
    title: Optional[str]
    file_name: Optional[str]
    mime_type: Optional[str]
    file_size: Optional[int]
    date: Optional[int]

    ####################################################
    download_url: str
    is_audio_file: bool  # whether the audio file is shown in the `audios` or `files/documents` section of telegram app
    valid_for_inline_search: bool
    """
     when an audio's title is None or the audio is shown in document section of
     telegram, then that audio could not be shown in telegram inline mode. Moreover, it should not have keyboard
     markups like `add_to_playlist`, etc... . On top of that, if any audio of this kind gets downloaded through
     query search, then, it cannot be shown in `download_history` section or any other sections that work in inline
     mode.
    """

    has_checked_forwarded_message: Optional[bool]
    has_checked_forwarded_message_at: Optional[int]

    is_forwarded: bool
    is_deleted: bool
    deleted_at: Optional[int]  # this is not always accurate
    is_edited: bool

    @classmethod
    def parse_key(
        cls,
        message: pyrogram.types.Message,
    ) -> str:
        if message.audio:
            _audio = message.audio
        elif message.document:
            _audio = message.document
        else:
            raise ValueError("Unexpected value for `message`: nor audio nor document")
        return f"{_audio.file_unique_id}:{message.chat.id}:{message.id}"

    @classmethod
    def parse(
        cls,
        telegram_message: pyrogram.types.Message,
    ) -> Optional["Audio"]:
        if not telegram_message or (telegram_message.audio is None and telegram_message.document is None):
            return None

        key = Audio.parse_key(telegram_message)

        if telegram_message.audio:
            _audio = telegram_message.audio
            is_audio_file = True
        elif telegram_message.document:
            _audio = telegram_message.document
            is_audio_file = False
        else:
            raise ValueError("Unexpected value for `message`: nor audio nor document")

        title = getattr(_audio, "title", None)

        # todo: check if the following statement is actually true
        valid_for_inline = True if title is not None and is_audio_file is not None else False

        is_forwarded = True if telegram_message.forward_date else False

        if telegram_message.forward_from:
            forwarded_from_chat_id = telegram_message.forward_from.id
        elif telegram_message.forward_from_chat:
            forwarded_from_chat_id = telegram_message.forward_from_chat.id
        else:
            forwarded_from_chat_id = None

        if is_forwarded:
            has_checked_forwarded_message = False
        else:
            has_checked_forwarded_message = None

        return Audio(
            key=key,
            chat_id=telegram_message.chat.id,
            message_id=telegram_message.id,
            message_caption=telegram_message.caption,
            message_date=get_timestamp(telegram_message.date) if telegram_message.date else None,
            message_edit_date=get_timestamp(telegram_message.edit_date) if telegram_message.edit_date else None,
            views=telegram_message.views,
            reactions=telegram_message.reactions,
            forward_date=get_timestamp(telegram_message.forward_date)
            if telegram_message.forward_date is not None
            else None,
            forward_from_chat_id=forwarded_from_chat_id,
            forward_from_message_id=telegram_message.forward_from_message_id,
            forward_signature=telegram_message.forward_signature,
            forward_sender_name=telegram_message.forward_sender_name,
            via_bot=True if telegram_message.via_bot else False,
            has_protected_content=telegram_message.has_protected_content,
            ################################
            file_unique_id=_audio.file_unique_id,
            duration=getattr(_audio, "duration", None),
            performer=getattr(_audio, "performer", None),
            title=title,
            file_name=_audio.file_name,
            mime_type=_audio.mime_type,
            file_size=_audio.file_size,
            date=get_timestamp(_audio.date) if _audio.date else None,
            ################################
            download_url=generate_token_urlsafe(),
            valid_for_inline_search=valid_for_inline,
            is_audio_file=is_audio_file,
            has_checked_forwarded_message=has_checked_forwarded_message,
            is_forwarded=is_forwarded,
            is_deleted=True if telegram_message.empty else False,
            is_edited=True if telegram_message.edit_date else False,
        )


######################################################################


class AudioMethods:
    def find_audio_by_download_url(
        self,
        download_url: str,
    ) -> Optional[Audio]:
        if download_url is None:
            return None

        audios = Audio.find({"download_url": download_url}, limit=1)
        if audios is None:
            return None
        else:
            audios = list(audios)
            if not len(audios):
                return None
            else:
                return audios[0]
