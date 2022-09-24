from .audio import Audio, AudioMethods
from .base_vertex import BaseVertex
from .chat import Chat, ChatMethods
from .dummy_vertex import DummyVertex, DummyVertexMethods
from .file import File, FileMethods
from .hashtag import Hashtag, HashTagMethods
from .hit import Hit, HitMethods
from .interaction import Interaction, InteractionMethods
from .keyword import Keyword, KeywordMethods
from .playlist import Playlist, PlaylistMethods
from .query import Query, QueryMethods
from .user import User, UserMethods
from .username import Username, UsernameMethods

vertex_classes = [
    Audio,
    Chat,
    DummyVertex,
    File,
    Hashtag,
    Hit,
    Interaction,
    Keyword,
    Playlist,
    Query,
    User,
    Username,
]


class ArangoVertexMethods(
    AudioMethods,
    ChatMethods,
    DummyVertexMethods,
    FileMethods,
    HashTagMethods,
    HitMethods,
    InteractionMethods,
    KeywordMethods,
    PlaylistMethods,
    QueryMethods,
    UserMethods,
    UsernameMethods,
):
    pass
