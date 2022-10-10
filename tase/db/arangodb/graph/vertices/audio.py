from __future__ import annotations

import copy
from typing import Optional, List, Generator, TYPE_CHECKING

import pyrogram
from arango import CursorEmptyError

from tase.common.preprocessing import clean_text
from tase.common.utils import (
    datetime_to_timestamp,
    get_now_timestamp,
    find_hashtags_in_text,
)
from tase.db.db_utils import (
    get_telegram_message_media_type,
    parse_audio_key,
    is_audio_valid_for_inline,
)
from tase.errors import (
    TelegramMessageWithNoAudio,
    InvalidToVertex,
    InvalidFromVertex,
    EdgeCreationFailed,
)
from tase.my_logger import logger
from .base_vertex import BaseVertex
from .hit import Hit
from .interaction import Interaction
from .user import User
from ...helpers import BitRateType

if TYPE_CHECKING:
    from .. import ArangoGraphMethods
from ...enums import TelegramAudioType, MentionSource, InteractionType


class Audio(BaseVertex):
    _collection_name = "audios"
    schema_version = 1

    _extra_do_not_update_fields = [
        "has_checked_forwarded_message_at",
        "deleted_at",
    ]

    chat_id: int
    message_id: int
    message_caption: Optional[str]
    raw_message_caption: Optional[str]
    message_date: Optional[int]
    message_edit_date: Optional[int]
    views: Optional[int]
    forward_date: Optional[int]
    forward_from_user_id: Optional[int]
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
    file_unique_id: Optional[str]
    duration: Optional[int]
    performer: Optional[str]
    raw_performer: Optional[str]
    title: Optional[str]
    raw_title: Optional[str]
    file_name: Optional[str]
    raw_file_name: Optional[str]
    mime_type: Optional[str]
    file_size: Optional[int]
    date: Optional[int]

    ####################################################
    audio_type: TelegramAudioType  # whether the audio file is shown in the `audios` or `files/documents` section of telegram app
    valid_for_inline_search: bool
    """
     when an audio's title is None or the audio is shown in document section of
     telegram, then that audio could not be shown in telegram inline mode. Moreover, it should not have keyboard
     markups like `add_to_playlist`, etc... . On top of that, if any audio of this kind gets downloaded through
     query search, then, it cannot be shown in `download_history` section or any other sections that work in inline
     mode.
    """

    estimated_bit_rate_type: BitRateType
    has_checked_forwarded_message: Optional[bool]
    has_checked_forwarded_message_at: Optional[int]

    is_forwarded: bool
    is_deleted: bool
    deleted_at: Optional[int]  # this is not always accurate
    is_edited: bool

    @classmethod
    def parse_key(
        cls,
        telegram_message: pyrogram.types.Message,
    ) -> Optional[str]:
        """
        Parse the `key` from the given `telegram_message` argument

        Parameters
        ----------
        telegram_message : pyrogram.types.Message
            Telegram message to parse the key from

        Returns
        -------
        str, optional
            Parsed key if the parsing was successful, otherwise return `None` if the `telegram_message` is `None`.

        """
        return parse_audio_key(telegram_message)

    @classmethod
    def parse(
        cls,
        telegram_message: pyrogram.types.Message,
    ) -> Optional[Audio]:
        """
        Parse an `Audio` from the given `telegram_message` argument.

        Parameters
        ----------
        telegram_message : pyrogram.types.Message
            Telegram message to parse the `Audio` from

        Returns
        -------
        Audio, optional
            Parsed `Audio` if parsing was successful, otherwise, return `None`.

        Raises
        ------
        TelegramMessageWithNoAudio
            If `telegram_message` argument does not contain any valid audio file.
        """
        if telegram_message is None:
            return None

        key = Audio.parse_key(telegram_message)

        audio, audio_type = get_telegram_message_media_type(telegram_message)
        if audio is None or audio_type == TelegramAudioType.NON_AUDIO:
            raise TelegramMessageWithNoAudio(
                telegram_message.id, telegram_message.chat.id
            )

        title = getattr(audio, "title", None)

        valid_for_inline = is_audio_valid_for_inline(audio, audio_type)

        is_forwarded = True if telegram_message.forward_date else False

        if telegram_message.forward_from_chat:
            forwarded_from_chat_id = telegram_message.forward_from_chat.id
        else:
            forwarded_from_chat_id = None

        if telegram_message.forward_from:
            forwarded_from_user_id = telegram_message.forward_from.id
        else:
            forwarded_from_user_id = None

        if is_forwarded and forwarded_from_chat_id is not None:
            has_checked_forwarded_message = False
        else:
            has_checked_forwarded_message = None

        raw_title = copy.copy(title)
        raw_caption = copy.copy(
            telegram_message.caption
            if telegram_message.caption
            else telegram_message.text
        )
        raw_performer = copy.copy(getattr(audio, "performer", None))
        raw_file_name = copy.copy(audio.file_name)

        title = clean_text(title)
        caption = clean_text(
            telegram_message.caption
            if telegram_message.caption
            else telegram_message.text
        )
        performer = clean_text(getattr(audio, "performer", None))
        file_name = clean_text(audio.file_name)

        duration = getattr(audio, "duration", None)

        return Audio(
            key=key,
            chat_id=telegram_message.chat.id,
            message_id=telegram_message.id,
            message_caption=caption,
            raw_message_caption=raw_caption,
            message_date=datetime_to_timestamp(telegram_message.date),
            message_edit_date=datetime_to_timestamp(telegram_message.edit_date),
            views=telegram_message.views,
            forward_date=datetime_to_timestamp(telegram_message.forward_date),
            forward_from_user_id=forwarded_from_user_id,
            forward_from_chat_id=forwarded_from_chat_id,
            forward_from_message_id=telegram_message.forward_from_message_id,
            forward_signature=telegram_message.forward_signature,
            forward_sender_name=telegram_message.forward_sender_name,
            via_bot=True if telegram_message.via_bot else False,
            has_protected_content=telegram_message.has_protected_content,
            ################################
            file_unique_id=audio.file_unique_id,
            duration=duration,
            performer=performer,
            raw_performer=raw_performer,
            title=title,
            raw_title=raw_title,
            file_name=file_name,
            raw_file_name=raw_file_name,
            mime_type=audio.mime_type,
            file_size=audio.file_size,
            date=datetime_to_timestamp(audio.date),
            ################################
            valid_for_inline_search=valid_for_inline,
            estimated_bit_rate_type=BitRateType.estimate(
                audio.file_size,
                duration,
            ),
            audio_type=audio_type,
            has_checked_forwarded_message=has_checked_forwarded_message,
            is_forwarded=is_forwarded,
            is_deleted=True if telegram_message.empty else False,
            is_edited=True if telegram_message.edit_date else False,
        )

    def mark_as_deleted(self) -> bool:
        """
        Mark the Audio the as deleted. This happens when the message is deleted in telegram.

        Returns
        -------
        bool
            Whether the operation was successful or not.

        """
        self_copy = self.copy(deep=True)
        self_copy.is_deleted = True
        self_copy.deleted_at = get_now_timestamp()
        return self.update(self_copy, reserve_non_updatable_fields=False)

    def mark_as_invalid(
        self,
        telegram_message: pyrogram.types.Message,
    ) -> bool:
        """
        Mark the audio as invalid since it has been edited in telegram and changed to non-audio file.

        Parameters
        ----------
        telegram_message : pyrogram.types.Message
            Telegram message to update the Audio by

        Returns
        -------
        bool
            Whether the update was successful or not.

        """
        if telegram_message is None:
            return False

        self_copy = self.copy(deep=True)
        self_copy.audio_type = TelegramAudioType.NON_AUDIO
        return self.update(self_copy, reserve_non_updatable_fields=True)


######################################################################


class AudioMethods:
    _get_audio_from_hit_query = (
        "for v,e in 1..1 outbound '@start_vertex' graph '@graph_name' options {order:'dfs', edgeCollections:['@has'], vertexCollections:['@audios']}"
        "   limit 1"
        "   return v"
    )

    _check_audio_validity_for_inline_mode = (
        "for hit in @hits"
        "   filter hit.download_url == '@hit_download_url'"
        "   for v,e in 1..1 outbound hit graph '@graph_name' options {order:'dfs', edgeCollections:['@has'], vertexCollections:['@audios']}"
        "       limit 1"
        "       return v.valid_for_inline_search"
    )

    _get_user_download_history_query = (
        "for dl_v,dl_e in 1..1 outbound '@start_vertex' graph '@graph_name' options {order:'dfs', edgeCollections:['@has'], vertexCollections:['@interactions']}"
        "   filter dl_v.type == @interaction_type"
        "   sort dl_e.created_at DESC"
        "   for aud_v,has_e in 1..1 outbound dl_v graph '@graph_name' options {order:'dfs', edgeCollections:['@has'], vertexCollections:['@audios']}"
        "       limit @offset, @limit"
        "       return aud_v"
    )

    _get_user_download_history_inline_query = (
        "for dl_v,dl_e in 1..1 outbound '@start_vertex' graph '@graph_name' options {order:'dfs', edgeCollections:['@has'], vertexCollections:['@interactions']}"
        "   filter dl_v.type == @interaction_type"
        "   sort dl_e.created_at DESC"
        "   for aud_v,has_e in 1..1 outbound dl_v graph '@graph_name' options {order:'dfs', edgeCollections:['@has'], vertexCollections:['@audios']}"
        "       filter aud_v.valid_for_inline_search == true"
        "       limit @offset, @limit"
        "       return aud_v"
    )

    _get_audios_by_keys = "return document(@audios, @audio_keys)"

    def create_audio(
        self: ArangoGraphMethods,
        telegram_message: pyrogram.types.Message,
    ) -> Optional[Audio]:
        """
        Create Audio alongside necessary vertices and edges in the ArangoDB.

        Parameters
        ----------
        telegram_message : pyrogram.types.Message
            Telegram message to create the Audio from

        Returns
        -------
        Audio, optional
            Audio if the creation was successful, otherwise, return None

        Raises
        ------
        EdgeCreationFailed
            If creation of the related edges was unsuccessful.
        """
        if telegram_message is None:
            return None

        try:
            audio, successful = Audio.insert(Audio.parse(telegram_message))
        except TelegramMessageWithNoAudio as e:
            # this message doesn't contain any valid audio file
            pass
        except Exception as e:
            logger.exception(e)
        else:
            if audio and successful:
                audio: Audio = audio

                hashtags = find_hashtags_in_text(
                    [
                        audio.raw_message_caption,
                        audio.raw_title,
                        audio.raw_performer,
                        audio.raw_file_name,
                    ],
                    [
                        MentionSource.MESSAGE_TEXT,
                        MentionSource.AUDIO_TITLE,
                        MentionSource.AUDIO_PERFORMER,
                        MentionSource.AUDIO_FILE_NAME
                        if audio.audio_type == TelegramAudioType.AUDIO_FILE
                        else MentionSource.DOCUMENT_FILE_NAME,
                    ],
                )

                for hashtag, start_index, mention_source in hashtags:
                    from tase.db.arangodb.graph.edges import HasHashtag

                    hashtag_vertex = self.get_or_create_hashtag(hashtag)
                    if hashtag_vertex:
                        has_hashtag = HasHashtag.get_or_create_edge(
                            audio,
                            hashtag_vertex,
                            mention_source,
                            start_index,
                        )
                        if has_hashtag is None:
                            raise EdgeCreationFailed(HasHashtag.__class__.__name__)
                    else:
                        pass

                chat = self.get_or_create_chat(telegram_message.chat)
                try:
                    from tase.db.arangodb.graph.edges import SentBy

                    sent_by_edge = SentBy.get_or_create_edge(audio, chat)
                    if sent_by_edge is None:
                        raise EdgeCreationFailed(SentBy.__class__.__name__)
                except (InvalidFromVertex, InvalidToVertex):
                    pass

                # since checking for audio file validation is done above, there is no need to it again.
                file = self.get_or_create_file(telegram_message)
                try:
                    from tase.db.arangodb.graph.edges import FileRef

                    file_ref_edge = FileRef.get_or_create_edge(audio, file)
                    if file_ref_edge is None:
                        raise EdgeCreationFailed(FileRef.__class__.__name__)
                except (InvalidFromVertex, InvalidToVertex):
                    pass

                if audio.is_forwarded:
                    if telegram_message.forward_from:
                        forwarded_from = self.get_or_create_user(
                            telegram_message.forward_from
                        )
                    elif telegram_message.forward_from_chat:
                        forwarded_from = self.get_or_create_chat(
                            telegram_message.forward_from_chat
                        )
                    else:
                        forwarded_from = None

                    if forwarded_from is not None:
                        try:
                            from tase.db.arangodb.graph.edges import ForwardedFrom

                            forwarded_from_edge = ForwardedFrom.get_or_create_edge(
                                audio, forwarded_from
                            )
                            if forwarded_from_edge is None:
                                raise EdgeCreationFailed(
                                    ForwardedFrom.__class__.__name__
                                )
                        except (InvalidFromVertex, InvalidToVertex):
                            pass

                    # todo: the `forwarded_from` edge from `audio` to the `original audio` must be checked later

                if audio.via_bot:
                    bot = self.get_or_create_user(telegram_message.via_bot)
                    try:
                        from tase.db.arangodb.graph.edges import ViaBot

                        via_bot_edge = ViaBot.get_or_create_edge(audio, bot)
                        if via_bot_edge is None:
                            raise EdgeCreationFailed(ViaBot.__class__.__name__)
                    except (InvalidFromVertex, InvalidToVertex):
                        pass

                return audio

        return None

    def get_or_create_audio(
        self,
        telegram_message: pyrogram.types.Message,
    ) -> Optional[Audio]:
        """
        Get Audio if it exists in ArangoDB, otherwise, create Audio alongside necessary vertices and edges in the
        ArangoDB.

        Parameters
        ----------
        telegram_message : pyrogram.types.Message
            Telegram message to create the Audio from

        Returns
        -------
        Audio, optional
            Audio if the operation was successful, otherwise, return None

        Raises
        ------
        EdgeCreationFailed
            If creation of the related edges was unsuccessful.
        """
        if telegram_message is None:
            return None

        audio = Audio.get(Audio.parse_key(telegram_message))
        if audio is None:
            audio = self.create_audio(telegram_message)

        return audio

    def update_or_create_audio(
        self,
        telegram_message: pyrogram.types.Message,
    ) -> Optional[Audio]:
        """
        Update Audio alongside necessary vertices and edges in the ArangoDB if it exists, otherwise, create it.

        Parameters
        ----------
        telegram_message : pyrogram.types.Message
            Telegram message to create the Audio from

        Returns
        -------
        Audio, optional
            Audio if the creation was successful, otherwise, return None

        Raises
        ------
        EdgeCreationFailed
            If creation of the related edges was unsuccessful.
        """
        if telegram_message is None:
            return None

        audio: Optional[Audio] = Audio.get(Audio.parse_key(telegram_message))

        if audio is not None:
            telegram_audio, audio_type = get_telegram_message_media_type(
                telegram_message
            )
            if telegram_audio is None or audio_type == TelegramAudioType.NON_AUDIO:
                # this message doesn't contain any valid audio file, check if there is a previous audio in the database
                # and check it as invalid audio.
                successful = audio.mark_as_invalid(telegram_message)
                if not successful:
                    # fixme: could not mark the audio as invalid, why?
                    pass
            else:
                # update the audio and its edges
                if telegram_message.empty:
                    # the message has been deleted, mark the audio as deleted in the database
                    deleted = audio.mark_as_deleted()
                    if not deleted:
                        # fixme: could not mark the audio as deleted, why?
                        pass
                else:
                    # the message has not been `deleted`, update remaining attributes
                    try:
                        updated = audio.update(Audio.parse(telegram_message))
                    except ValueError:
                        updated = False

        else:
            audio = self.create_audio(telegram_message)

        return audio

    def find_audio_by_download_url(
        self,
        download_url: str,
    ) -> Optional[Audio]:
        """
        Get Audio by `download_url` in the ArangoDB

        Parameters
        ----------
        download_url : str
            Download URL to get the Audio from

        Returns
        -------
        Audio, optional
            Audio if it exists with the given `download_url` parameter, otherwise, return None

        """
        if download_url is None:
            return None

        return Audio.find_one({"download_url": download_url})

    def get_audio_from_hit(
        self,
        hit: Hit,
    ) -> Optional[Audio]:
        """
        Get an `Audio` vertex from the given `Hit` vertex

        Parameters
        ----------
        hit : Hit
            Hit to get the audio from.

        Returns
        -------
        Audio, optional
            Audio if operation was successful, otherwise, return None

        Raises
        ------
        ValueError
            If the given `Hit` vertex has more than one linked `Audio` vertices.
        """
        if hit is None:
            return

        from tase.db.arangodb.graph.edges import Has

        cursor = Audio.execute_query(
            self._get_audio_from_hit_query,
            bind_vars={
                "start_vertex": hit.id,
                "audios": Audio._collection_name,
                "has": Has._collection_name,
            },
        )
        if cursor is not None and len(cursor):
            if len(cursor) > 1:
                raise ValueError(
                    f"Hit with id `{hit.id}` have more than one linked audios."
                )
            else:
                try:
                    doc = cursor.pop()
                except CursorEmptyError:
                    pass
                except Exception as e:
                    logger.exception(e)
                else:
                    return Audio.from_collection(doc)

    def is_audio_valid_for_inline_mode(
        self,
        hit_download_url: str,
    ) -> Optional[bool]:
        """
        Check for inline validity of an `Audio` vertex from a `Hit` vertex `download_url`

        Parameters
        ----------
        hit_download_url : str
            Download URL of a hit vertex connected to the audio vertex

        Returns
        -------
        bool, optional
            Whether the audio vertex is valid for inline search if it exists in the database, otherwise return None

        """
        if hit_download_url is None or not len(hit_download_url):
            return False

        from tase.db.arangodb.graph.edges import Has

        cursor = Audio.execute_query(
            self._check_audio_validity_for_inline_mode,
            bind_vars={
                "hits": Hit._collection_name,
                "hit_download_url": hit_download_url,
                "audios": Audio._collection_name,
                "has": Has._collection_name,
            },
        )
        if cursor is not None and len(cursor):
            try:
                is_valid: bool = cursor.pop()
            except CursorEmptyError:
                pass
            except Exception as e:
                logger.exception(e)
            else:
                return is_valid

        return False

    def get_user_download_history(
        self,
        user: User,
        filter_by_valid_for_inline_search: bool = True,
        offset: int = 0,
        limit: int = 15,
    ) -> Generator[Audio, None, None]:
        """
        Get `User` download history.

        Parameters
        ----------
        user : User
            User to get the download history
        filter_by_valid_for_inline_search : bool, default : True
            Whether to only get audio files that are valid to be shown in inline mode
        offset : int, default : 0
            Offset to get the download history query after
        limit : int, default : 15
            Number of `Audio`s to query

        Yields
        ------
        Audio
            Audios that the given user has downloaded

        """
        if user is None:
            return

        from tase.db.arangodb.graph.edges import Has

        cursor = Audio.execute_query(
            self._get_user_download_history_inline_query
            if filter_by_valid_for_inline_search
            else self._get_user_download_history_query,
            bind_vars={
                "start_vertex": user.id,
                "has": Has._collection_name,
                "audios": Audio._collection_name,
                "interactions": Interaction._collection_name,
                "interaction_type": InteractionType.DOWNLOAD.value,
                "offset": offset,
                "limit": limit,
            },
        )
        if cursor is not None and len(cursor):
            for doc in cursor:
                yield Audio.from_collection(doc)

    def get_audios_from_keys(
        self,
        keys: List[str],
    ) -> Generator[Audio, None, None]:
        """
        Get a list of Audios from a list of keys.

        Parameters
        ----------
        keys : List[str]
            List of keys to get the audios from.

        Yields
        ------
        Audio
            List of Audios if operation was successful, otherwise, return None

        """
        if keys is None or not len(keys):
            return

        cursor = Audio.execute_query(
            self._get_audios_by_keys,
            bind_vars={
                "audios": Audio._collection_name,
                "audio_keys": keys,
            },
        )
        if cursor is not None and len(cursor):
            try:
                audios_raw = cursor.pop()
            except CursorEmptyError:
                pass
            except Exception as e:
                logger.exception(e)
            else:
                for doc in audios_raw:
                    yield Audio.from_collection(doc)
