from pydantic import Field

from .base_indexer_metadata import BaseIndexerMetadata


class UsernameExtractorMetadata(BaseIndexerMetadata):
    """
    This class is used to store username extractor metadata and is not vertex by itself
    """

    direct_self_mention_count: int = Field(default=0)
    direct_raw_mention_count: int = Field(default=0)
    direct_valid_mention_count: int = Field(default=0)
    direct_valid_channel_mention_count: int = Field(default=0)
    direct_valid_supergroup_mention_count: int = Field(default=0)
    direct_valid_bot_mention_count: int = Field(default=0)
    direct_valid_user_mention_count: int = Field(default=0)

    undirect_self_mention_count: int = Field(default=0)
    undirect_raw_mention_count: int = Field(default=0)
    undirect_valid_mention_count: int = Field(default=0)
    undirect_valid_channel_mention_count: int = Field(default=0)
    undirect_valid_supergroup_mention_count: int = Field(default=0)
    undirect_valid_bot_mention_count: int = Field(default=0)
    undirect_valid_user_mention_count: int = Field(default=0)

    def reset_counters(self):
        super(UsernameExtractorMetadata, self).reset_counters()

        self.direct_self_mention_count = 0
        self.direct_raw_mention_count = 0
        self.direct_valid_mention_count = 0
        self.direct_valid_channel_mention_count = 0
        self.direct_valid_supergroup_mention_count = 0
        self.direct_valid_bot_mention_count = 0
        self.direct_valid_user_mention_count = 0

        self.undirect_self_mention_count = 0
        self.undirect_raw_mention_count = 0
        self.undirect_valid_mention_count = 0
        self.undirect_valid_channel_mention_count = 0
        self.undirect_valid_supergroup_mention_count = 0
        self.undirect_valid_bot_mention_count = 0
        self.undirect_valid_user_mention_count = 0

    def __add__(self, other:"UsernameExtractorMetadata"):
        super(UsernameExtractorMetadata, self).__add__(other)

        self.direct_self_mention_count += other.direct_self_mention_count
        self.direct_raw_mention_count += other.direct_raw_mention_count
        self.direct_valid_mention_count += other.direct_valid_mention_count
        self.direct_valid_channel_mention_count += other.direct_valid_channel_mention_count
        self.direct_valid_supergroup_mention_count += other.direct_valid_supergroup_mention_count
        self.direct_valid_bot_mention_count += other.direct_valid_bot_mention_count
        self.direct_valid_user_mention_count += other.direct_valid_user_mention_count

        self.undirect_self_mention_count += other.undirect_self_mention_count
        self.undirect_raw_mention_count += other.undirect_raw_mention_count
        self.undirect_valid_mention_count += other.undirect_valid_mention_count
        self.undirect_valid_channel_mention_count += other.undirect_valid_channel_mention_count
        self.undirect_valid_supergroup_mention_count += other.undirect_valid_supergroup_mention_count
        self.undirect_valid_bot_mention_count += other.undirect_valid_bot_mention_count
        self.undirect_valid_user_mention_count += other.undirect_valid_user_mention_count

        return self
