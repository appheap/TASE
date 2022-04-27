from .archived_audio import ArchivedAudio
from .base_edge import BaseEdge
from .contact_of import ContactOf
from .creator import Creator
from .downloaded import Downloaded
from .downloaded_audio import DownloadedAudio
from .downloaded_from_bot import DownloadedFromBot
from .file_ref import FileRef
from .from_user import FromUser
from .has_audio import HasAudio
from .has_playlist import HasPlaylist
from .linked_chat import LinkedChat
from .member_of import MemberOf
from .sender_chat import SenderChat
from .to_bot import ToBot

__all__ = [
    'ArchivedAudio',
    'BaseEdge',
    'ContactOf',
    'Creator',
    'Downloaded',
    'DownloadedAudio',
    'DownloadedFromBot',
    'FileRef',
    'FromUser',
    'HasAudio',
    'HasPlaylist',
    'LinkedChat',
    'MemberOf',
    'SenderChat',
    'ToBot',
]

edges = [
    ArchivedAudio,
    ContactOf,
    Creator,
    Downloaded,
    DownloadedAudio,
    DownloadedFromBot,
    FileRef,
    FromUser,
    HasAudio,
    HasPlaylist,
    LinkedChat,
    MemberOf,
    SenderChat,
    ToBot,
]
