from typing import Optional

import pyrogram
from pydantic import BaseModel


class BaseInlineItem(BaseModel):
    @classmethod
    def get_item(cls, *args, **kwargs) -> Optional["pyrogram.types.InlineQueryResult"]:
        raise NotImplementedError
