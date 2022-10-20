from __future__ import annotations

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

    indirect_self_mention_count: int = Field(default=0)
    indirect_raw_mention_count: int = Field(default=0)
    indirect_valid_mention_count: int = Field(default=0)
    indirect_valid_channel_mention_count: int = Field(default=0)
    indirect_valid_supergroup_mention_count: int = Field(default=0)
    indirect_valid_bot_mention_count: int = Field(default=0)
    indirect_valid_user_mention_count: int = Field(default=0)

    def reset_counters(self):
        super(UsernameExtractorMetadata, self).reset_counters()

        self.direct_self_mention_count = 0
        self.direct_raw_mention_count = 0
        self.direct_valid_mention_count = 0
        self.direct_valid_channel_mention_count = 0
        self.direct_valid_supergroup_mention_count = 0
        self.direct_valid_bot_mention_count = 0
        self.direct_valid_user_mention_count = 0

        self.indirect_self_mention_count = 0
        self.indirect_raw_mention_count = 0
        self.indirect_valid_mention_count = 0
        self.indirect_valid_channel_mention_count = 0
        self.indirect_valid_supergroup_mention_count = 0
        self.indirect_valid_bot_mention_count = 0
        self.indirect_valid_user_mention_count = 0

    def log(self, input_num: float) -> float:
        if input_num == 0:
            return 0.0
        return math.log(input_num, 1000_000_000_000)

    def update_score(self):
        try:
            direct_raw_mention_ratio = self.direct_raw_mention_count / (self.direct_raw_mention_count + self.direct_self_mention_count)
        except ZeroDivisionError:
            direct_raw_mention_ratio = 0.0

        try:
            indirect_raw_mention_ratio = self.indirect_raw_mention_count / (self.indirect_raw_mention_count + self.indirect_self_mention_count)
        except ZeroDivisionError:
            indirect_raw_mention_ratio = 0.0

        #####################################################

        try:
            direct_valid_mention_ratio = self.direct_valid_mention_count / self.direct_raw_mention_count
        except ZeroDivisionError:
            direct_valid_mention_ratio = 0.0

        try:
            indirect_valid_mention_ratio = self.indirect_valid_mention_count / self.indirect_raw_mention_count
        except ZeroDivisionError:
            indirect_valid_mention_ratio = 0.0

        #####################################################
        try:
            direct_valid_channel_mention_ratio = self.direct_valid_channel_mention_count / self.direct_valid_mention_count
        except ZeroDivisionError:
            direct_valid_channel_mention_ratio = 0.0

        try:
            indirect_valid_channel_mention_ratio = self.indirect_valid_channel_mention_count / self.indirect_valid_mention_count
        except ZeroDivisionError:
            indirect_valid_channel_mention_ratio = 0.0

        #####################################################

        try:
            direct_valid_supergroup_mention_ratio = self.direct_valid_supergroup_mention_count / self.direct_valid_mention_count
        except ZeroDivisionError:
            direct_valid_supergroup_mention_ratio = 0.0

        try:
            indirect_valid_channel_mention_ratio = self.indirect_valid_channel_mention_count / self.indirect_valid_mention_count
        except ZeroDivisionError:
            indirect_valid_channel_mention_ratio = 0.0

        #####################################################

        try:
            direct_valid_supergroup_mention_ratio = self.direct_valid_supergroup_mention_count / self.direct_valid_mention_count
        except ZeroDivisionError:
            direct_valid_supergroup_mention_ratio = 0.0

        try:
            indirect_valid_supergroup_mention_ratio = self.indirect_valid_supergroup_mention_count / self.indirect_valid_mention_count
        except ZeroDivisionError:
            indirect_valid_supergroup_mention_ratio = 0.0

        #####################################################

        try:
            direct_valid_bot_mention_ratio = self.direct_valid_bot_mention_count / self.direct_valid_mention_count
        except ZeroDivisionError:
            direct_valid_bot_mention_ratio = 0.0

        try:
            indirect_valid_bot_mention_ratio = self.indirect_valid_bot_mention_count / self.indirect_valid_mention_count
        except ZeroDivisionError:
            indirect_valid_bot_mention_ratio = 0.0

        #####################################################

        try:
            direct_valid_user_mention_ratio = self.direct_valid_user_mention_count / self.direct_valid_mention_count
        except ZeroDivisionError:
            direct_valid_user_mention_ratio = 0.0

        try:
            indirect_valid_user_mention_ratio = self.indirect_valid_user_mention_count / self.indirect_valid_mention_count
        except ZeroDivisionError:
            indirect_valid_user_mention_ratio = 0.0

        #####################################################

        ratio = self.log(self.direct_raw_mention_count)

        # self.score = (ratio * 2 + direct_raw_mention_ratio) / 3

    def update_metadata(
        self,
        metadata: UsernameExtractorMetadata,
    ) -> UsernameExtractorMetadata:
        super(UsernameExtractorMetadata, self).update_metadata(metadata)

        if metadata is None or not isinstance(metadata, UsernameExtractorMetadata):
            return self

        self.direct_self_mention_count += metadata.direct_self_mention_count
        self.direct_raw_mention_count += metadata.direct_raw_mention_count
        self.direct_valid_mention_count += metadata.direct_valid_mention_count
        self.direct_valid_channel_mention_count += metadata.direct_valid_channel_mention_count
        self.direct_valid_supergroup_mention_count += metadata.direct_valid_supergroup_mention_count
        self.direct_valid_bot_mention_count += metadata.direct_valid_bot_mention_count
        self.direct_valid_user_mention_count += metadata.direct_valid_user_mention_count

        self.indirect_self_mention_count += metadata.indirect_self_mention_count
        self.indirect_raw_mention_count += metadata.indirect_raw_mention_count
        self.indirect_valid_mention_count += metadata.indirect_valid_mention_count
        self.indirect_valid_channel_mention_count += metadata.indirect_valid_channel_mention_count
        self.indirect_valid_supergroup_mention_count += metadata.indirect_valid_supergroup_mention_count
        self.indirect_valid_bot_mention_count += metadata.indirect_valid_bot_mention_count
        self.indirect_valid_user_mention_count += metadata.indirect_valid_user_mention_count

        return self
