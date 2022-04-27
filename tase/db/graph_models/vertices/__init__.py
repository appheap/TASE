from .audio import Audio
from .base_vertex import BaseVertex
from .chat import Chat
from .download import Download
from .file import File
from .inline_query import InlineQuery
from .playlist import Playlist
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
    User,
]