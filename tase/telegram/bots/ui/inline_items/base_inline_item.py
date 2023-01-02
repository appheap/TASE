from typing import Optional

import pyrogram
from pydantic import BaseModel, Field

from tase.telegram.bots.ui.base import InlineItemType


class BaseInlineItem(BaseModel):
    @classmethod
    def get_item(cls, *args, **kwargs) -> Optional[pyrogram.types.InlineQueryResult]:
        raise NotImplementedError

    __type__: InlineItemType = Field(default=InlineItemType.UNKNOWN)

    @classmethod
    def get_type_value(cls) -> int:
        return cls.__type__.value

    @classmethod
    def get_item_info_from_id_string(cls) -> None:
        pass
