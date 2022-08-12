from pydantic import Field

from .base_indexer_metadata import BaseIndexerMetadata


class UsernameExtractorMetadata(BaseIndexerMetadata):
    """
    This class is used to store username extractor metadata and is not vertex by itself
    """

    direct_self_mention_count: int = Field(default=0)
    direct_raw_mention_count: int = Field(default=0)
    direct_valid_mention_count: int = Field(default=0)

    undirect_self_mention_count: int = Field(default=0)
    undirect_raw_mention_count: int = Field(default=0)
    undirect_valid_mention_count: int = Field(default=0)
