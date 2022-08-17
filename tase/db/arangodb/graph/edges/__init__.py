from .archived_audio import ArchivedAudio, ArchivedAudioMethods
from .base_edge import BaseEdge
from .downloaded import Downloaded, DownloadedMethods
from .file_ref import FileRef, FileRefMethods
from .from_bot import FromBot, FromBotMethods
from .from_hit import FromHit, FromHitMethods
from .had import Had, HadMethods
from .has import Has, HasMethods
from .has_made import HasMade, HasMadeMethods
from .is_contact_of import IsContactOf, IsContactOfMethods
from .is_creator_of import IsCreatorOf, IsCreatorOfMethods
from .is_member_of import IsMemberOf, IsMemberOfMethods
from .linked_chat import LinkedChat, LinkedChatMethods
from .mentions import Mentions, MentionsMethods
from .sent_by import SentBy, SentByMethods
from .to_bot import ToBot, ToBotMethods

edge_classes = [
    ArchivedAudio,
    Downloaded,
    FileRef,
    FromBot,
    FromHit,
    Had,
    Has,
    HasMade,
    IsContactOf,
    IsCreatorOf,
    IsMemberOf,
    LinkedChat,
    Mentions,
    SentBy,
    ToBot,
]


class ArangoEdgeMethods(
    ArchivedAudio,
    DownloadedMethods,
    FileRefMethods,
    FromBotMethods,
    FromHitMethods,
    HadMethods,
    HasMethods,
    HasMadeMethods,
    IsContactOfMethods,
    IsCreatorOfMethods,
    IsMemberOfMethods,
    LinkedChatMethods,
    MentionsMethods,
    SentByMethods,
    ToBotMethods,
):
    pass
