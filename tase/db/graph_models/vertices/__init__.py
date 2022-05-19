from .audio import Audio
from .base_vertex import BaseVertex
from .chat import Chat
from .download import Download
from .file import File
from .hit import Hit
from .inline_query import InlineQuery
from .playlist import Playlist
from .query import Query
from .query_keyword import QueryKeyword
from .restriction import Restriction
from .user import User

vertices = [
    Audio,
    Chat,
    Download,
    File,
    Hit,
    InlineQuery,
    Playlist,
    Query,
    QueryKeyword,
    User,
]

__all__ = [
    'Audio',
    'BaseVertex',
    'Chat',
    'Download',
    'File',
    'Hit',
    'InlineQuery',
    'Playlist',
    'Query',
    'QueryKeyword',
    'Restriction',
    'User',
    'vertices',

]
