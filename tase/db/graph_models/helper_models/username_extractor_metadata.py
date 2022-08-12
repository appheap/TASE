import math

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

    def __add__(self, other: "UsernameExtractorMetadata"):
        super(UsernameExtractorMetadata, self).__add__(other)

        if self.last_message_offset_id < other.last_message_offset_id:
            older = self
            newer = other
        elif self.last_message_offset_id > other.last_message_offset_id:
            older = other
            newer = self
        else:
            return self

        older.direct_self_mention_count += newer.direct_self_mention_count
        older.direct_raw_mention_count += newer.direct_raw_mention_count
        older.direct_valid_mention_count += newer.direct_valid_mention_count
        older.direct_valid_channel_mention_count += newer.direct_valid_channel_mention_count
        older.direct_valid_supergroup_mention_count += newer.direct_valid_supergroup_mention_count
        older.direct_valid_bot_mention_count += newer.direct_valid_bot_mention_count
        older.direct_valid_user_mention_count += newer.direct_valid_user_mention_count

        older.undirect_self_mention_count += newer.undirect_self_mention_count
        older.undirect_raw_mention_count += newer.undirect_raw_mention_count
        older.undirect_valid_mention_count += newer.undirect_valid_mention_count
        older.undirect_valid_channel_mention_count += newer.undirect_valid_channel_mention_count
        older.undirect_valid_supergroup_mention_count += newer.undirect_valid_supergroup_mention_count
        older.undirect_valid_bot_mention_count += newer.undirect_valid_bot_mention_count
        older.undirect_valid_user_mention_count += newer.undirect_valid_user_mention_count

        return older

    def update_score(self):
        try:
            mention_ratio = self.direct_raw_mention_count / (
                self.direct_raw_mention_count + self.direct_self_mention_count
            )
        except ZeroDivisionError:
            mention_ratio = 0.0

        ratio = math.log(self.direct_raw_mention_count, 1000_000_000_000) if self.direct_raw_mention_count else 0

        self.score = (ratio * 2 + mention_ratio) / 3
