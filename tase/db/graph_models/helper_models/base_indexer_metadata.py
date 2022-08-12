from pydantic import BaseModel, Field


class BaseIndexerMetadata(BaseModel):
    """
    This class is used to store indexer metadata and is not vertex by itself
    """

    score: float = Field(default=0.0)
    last_message_offset_id: int = Field(default=1)
    last_message_offset_date: int = Field(default=0)
    message_count: int = Field(default=0)

    def reset_counters(self):
        self.message_count = 0

    def __add__(self, other: "BaseIndexerMetadata"):
        self.message_count += other.message_count
        if self.last_message_offset_id < other.last_message_offset_id:
            self.last_message_offset_id = other.last_message_offset_id
            self.last_message_offset_date = other.last_message_offset_date
            self.score = other.score

        return self
