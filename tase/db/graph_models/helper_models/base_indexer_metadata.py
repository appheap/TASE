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
        if self.last_message_offset_id < other.last_message_offset_id:
            older = self
            newer = other
        elif self.last_message_offset_id > other.last_message_offset_id:
            older = other
            newer = self
        else:
            return self

        older.last_message_offset_id = newer.last_message_offset_id
        older.last_message_offset_date = newer.last_message_offset_date
        older.score = newer.score
        older.message_count += newer.message_count

        return older

    def update_score(self):
        raise NotImplementedError
