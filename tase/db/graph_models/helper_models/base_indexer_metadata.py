from pydantic import BaseModel, Field


class BaseIndexerMetadata(BaseModel):
    """
    This class is used to store indexer metadata and is not vertex by itself
    """

    score: float = Field(default=0.0)
    last_message_offset_id: int = Field(default=1)
    last_message_offset_date: int = Field(default=0)
    message_count: int = Field(default=0)
