from .audio_vertex_does_not_exists import AudioVertexDoesNotExist
from .edge_creation_failed import EdgeCreationFailed
from .edge_deletion_failed import EdgeDeletionFailed
from .hit_does_not_exists import HitDoesNotExists
from .hit_no_linked_audio import HitNoLinkedAudio
from .hit_no_linked_playlist import HitNoLinkedPlaylist
from .invalid_audio_for_inline_mode import InvalidAudioForInlineMode
from .invalid_from_vertex import InvalidFromVertex
from .invalid_to_vertex import InvalidToVertex
from .not_base_collection_document_instance import NotBaseCollectionDocumentInstance
from .not_enough_ram_error import NotEnoughRamError
from .not_soft_deletable_subclass import NotSoftDeletableSubclass
from .null_chat_type import NullChatType
from .null_telegram_inline_query import NullTelegramInlineQuery
from .param_not_provided import ParamNotProvided
from .playlist_does_not_exists import PlaylistDoesNotExists
from .tase_error import TASEError
from .telegram_message_with_no_audio import TelegramMessageWithNoAudio
from .update_retry_count_failed import UpdateRetryCountFailed

__all__ = [
    "AudioVertexDoesNotExist",
    "EdgeCreationFailed",
    "EdgeDeletionFailed",
    "HitDoesNotExists",
    "HitNoLinkedAudio",
    "HitNoLinkedPlaylist",
    "InvalidAudioForInlineMode",
    "InvalidFromVertex",
    "InvalidToVertex",
    "NotBaseCollectionDocumentInstance",
    "NotEnoughRamError",
    "NotSoftDeletableSubclass",
    "NullChatType",
    "NullTelegramInlineQuery",
    "ParamNotProvided",
    "PlaylistDoesNotExists",
    "TASEError",
    "TelegramMessageWithNoAudio",
    "UpdateRetryCountFailed",
]
