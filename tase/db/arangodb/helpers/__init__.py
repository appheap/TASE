"""
This package is used to include store that are neither `vertex` nor `edge`, but they are being used in either a
`vertex` or an `edge`.
"""
from .audio_doc_indexer_metadata import AudioDocIndexerMetadata
from .audio_indexer_metadata import AudioIndexerMetadata
from .audio_interaction_count import AudioInteractionCount
from .audio_keyboard_status import AudioKeyboardStatus
from .base_indexer_metadata import BaseIndexerMetadata
from .bit_rate_type import BitRateType
from .elastic_query_metadata import ElasticQueryMetadata
from .hit_count import HitCount
from .hit_metadata import BaseHitMetadata, AudioHitMetadata, PlaylistAudioHitMetadata, PlaylistHitMetadata, HitMetadata
from .inline_query_metadata import InlineQueryMetadata
from .playlist_interaction_count import PlaylistInteractionCount
from .public_playlist_subscription_count import PublicPlaylistSubscriptionCount
from .restriction import Restriction
from .username_extractor_metadata import UsernameExtractorMetadata
