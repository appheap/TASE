from .archived_audio import ArchivedAudio, ArchivedAudioMethods
from .base_edge import BaseEdge, EdgeEndsValidator
from .downloaded import Downloaded, DownloadedMethods
from .file_ref import FileRef, FileRefMethods
from .forwarded_from import ForwardedFrom, ForwardedFromMethods
from .from_bot import FromBot, FromBotMethods
from .from_hit import FromHit, FromHitMethods
from .had import Had, HadMethods
from .has import Has, HasMethods
from .has_hashtag import HasHashtag, HasHashtagMethods
from .has_made import HasMade, HasMadeMethods
from .linked_chat import LinkedChat, LinkedChatMethods
from .mentions import Mentions, MentionsMethods
from .sent_by import SentBy, SentByMethods
from .to_bot import ToBot, ToBotMethods
from .via_bot import ViaBot, ViaBotMethods

edge_classes = [
    ArchivedAudio,
    Downloaded,
    FileRef,
    ForwardedFrom,
    FromBot,
    FromHit,
    Had,
    Has,
    HasHashtag,
    HasMade,
    LinkedChat,
    Mentions,
    SentBy,
    ToBot,
    ViaBot,
]


class ArangoEdgeMethods(
    ArchivedAudioMethods,
    DownloadedMethods,
    FileRefMethods,
    ForwardedFromMethods,
    FromBotMethods,
    FromHitMethods,
    HadMethods,
    HasMethods,
    HasHashtagMethods,
    HasMadeMethods,
    LinkedChatMethods,
    MentionsMethods,
    SentByMethods,
    ToBotMethods,
    ViaBotMethods,
):
    pass
