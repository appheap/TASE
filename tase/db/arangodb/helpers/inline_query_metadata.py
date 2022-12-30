from typing import Optional

from pydantic import Field

from ..base import BaseCollectionAttributes
from ..enums import ChatType, InlineQueryType


class InlineQueryMetadata(BaseCollectionAttributes):
    query_id: str
    chat_type: ChatType

    offset: str
    next_offset: Optional[str]

    type: InlineQueryType = Field(default=InlineQueryType.AUDIO_SEARCH)
