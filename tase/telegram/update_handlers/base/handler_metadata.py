from typing import Callable, Optional, Type

from pydantic import BaseModel
from pyrogram import filters


class HandlerMetadata(BaseModel):
    cls: Type
    callback: Callable
    filters: Optional[filters.Filter]
    has_filter: bool = True
    group: int = 0

    class Config:
        arbitrary_types_allowed = True
