from typing import Optional

from pydantic import BaseModel, Field

from ..enums import ChatType, InlineQueryType


class InlineQueryMetadata(BaseModel):
    query_id: str
    chat_type: ChatType

    offset: str
    next_offset: Optional[str]

    type: InlineQueryType = Field(default=InlineQueryType.SEARCH)
