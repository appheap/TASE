from .archived_audio import ArchivedAudio
from .base_edge import BaseEdge
from .downloaded import Downloaded
from .file_ref import FileRef
from .from_bot import FromBot
from .from_hit import FromHit
from .has import Has
from .has_made import HasMade
from .is_contact_of import IsContactOf
from .is_creator_of import IsCreatorOf
from .is_member_of import IsMemberOf
from .linked_chat import LinkedChat
from .sent_by import SentBy
from .to_bot import ToBot

__all__ = [
    'ArchivedAudio',
    'BaseEdge',
    'Downloaded',
    'FileRef',
    'FromBot',
    'FromHit',
    'Has',
    'HasMade',
    'IsContactOf',
    'IsCreatorOf',
    'IsMemberOf',
    'LinkedChat',
    'SentBy',
    'ToBot',
]

edges = [
    ArchivedAudio,
    Downloaded,
    FileRef,
    FromBot,
    FromHit,
    Has,
    HasMade,
    IsContactOf,
    IsCreatorOf,
    IsMemberOf,
    LinkedChat,
    SentBy,
    ToBot,
]
