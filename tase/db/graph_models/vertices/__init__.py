from .audio import Audio
from .base_vertex import BaseVertex
from .chat import Chat
from .download import Download
from .file import File
from .inline_query import InlineQuery
from .playlist import Playlist
from .query import Query
from .restriction import Restriction
from .user import User

__all__ = [
    'Audio',
    'BaseVertex',
    'Chat',
    'Download',
    'File',
    'InlineQuery',
    'Playlist',
    'Query',
    'Restriction',
    'User',
]

vertices = [
    Audio,
    Chat,
    Download,
    File,
    InlineQuery,
    Playlist,
    Query,
    User,
]
