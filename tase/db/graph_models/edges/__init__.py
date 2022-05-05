from .archived_audio import ArchivedAudio
from .base_edge import BaseEdge
from .contact_of import ContactOf
from .creator import Creator
from .downloaded import Downloaded
from .downloaded_audio import DownloadedAudio
from .downloaded_from_bot import DownloadedFromBot
from .file_ref import FileRef
from .from_hit import FromHit
from .from_user import FromUser
from .has_audio import HasAudio
from .has_playlist import HasPlaylist
from .has_hit import HasHit
from .linked_chat import LinkedChat
from .member_of import MemberOf
from .sender_chat import SenderChat
from .to_bot import ToBot
from .to_query_keyword import ToQueryKeyword

__all__ = [
    'ArchivedAudio',
    'BaseEdge',
    'ContactOf',
    'Creator',
    'Downloaded',
    'DownloadedAudio',
    'DownloadedFromBot',
    'FileRef',
    'FromHit',
    'FromUser',
    'HasAudio',
    'HasPlaylist',
    'HasHit',
    'LinkedChat',
    'MemberOf',
    'SenderChat',
    'ToBot',
    'ToQueryKeyword',
]

edges = [
    ArchivedAudio,
    ContactOf,
    Creator,
    Downloaded,
    DownloadedAudio,
    DownloadedFromBot,
    FileRef,
    FromHit,
    FromUser,
    HasAudio,
    HasPlaylist,
    HasHit,
    LinkedChat,
    MemberOf,
    SenderChat,
    ToBot,
    ToQueryKeyword,
]
