from .audio import Audio, AudioMethods
from .audio_interaction import AudioInteraction, AudioInteractionMethods
from .base_vertex import BaseVertex
from .chat import Chat, ChatMethods
from .dummy_vertex import DummyVertex, DummyVertexMethods
from .file import File, FileMethods
from .hashtag import Hashtag, HashTagMethods
from .hit import Hit, HitMethods
from .keyword import Keyword, KeywordMethods
from .playlist import Playlist, PlaylistMethods
from .query import Query, QueryMethods
from .user import User, UserMethods
from .username import Username, UsernameMethods

vertex_classes = [
    Audio,
    AudioInteraction,
    Chat,
    DummyVertex,
    File,
    Hashtag,
    Hit,
    Keyword,
    Playlist,
    Query,
    User,
    Username,
]


class ArangoVertexMethods(
    AudioMethods,
    AudioInteractionMethods,
    ChatMethods,
    DummyVertexMethods,
    FileMethods,
    HashTagMethods,
    HitMethods,
    KeywordMethods,
    PlaylistMethods,
    QueryMethods,
    UserMethods,
    UsernameMethods,
):
    pass
