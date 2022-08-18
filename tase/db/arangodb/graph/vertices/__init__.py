from .audio import Audio, AudioMethods
from .base_vertex import BaseVertex
from .chat import Chat, ChatMethods
from .download import Download, DownloadMethods
from .dummy_vertex import DummyVertex, DummyVertexMethods
from .file import File, FileMethods
from .hit import Hit, HitMethods
from .inline_query import InlineQuery, InlineQueryMethods
from .keyword import Keyword, KeywordMethods
from .playlist import Playlist, PlaylistMethods
from .query import Query, QueryMethods
from .user import User, UserMethods
from .username import Username, UsernameMethods

vertex_classes = [
    Audio,
    Chat,
    Download,
    DummyVertex,
    File,
    Hit,
    InlineQuery,
    Keyword,
    Playlist,
    Query,
    User,
    Username,
]


class ArangoVertexMethods(
    AudioMethods,
    ChatMethods,
    DownloadMethods,
    DummyVertexMethods,
    FileMethods,
    HitMethods,
    InlineQueryMethods,
    KeywordMethods,
    PlaylistMethods,
    QueryMethods,
    UserMethods,
    UsernameMethods,
):
    pass
