from typing import Any, List, Optional

import pyrogram
from pydantic import BaseModel, Field
from pyrogram.errors import QueryIdInvalid, BadRequest

from tase.errors import NullTelegramInlineQuery
from tase.my_logger import logger


class CustomInlineQueryResult(BaseModel):
    results: List[pyrogram.types.InlineQueryResult] = Field(default_factory=list)
    next_offset: Optional[int]
    cache_time: int = Field(default=1)
    from_: int = Field(default=0)
    extra_items: int = Field(default=0)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, inline_query, **data: Any):
        super().__init__(**data)

        if inline_query is None:
            self.from_ = 0

        if inline_query.offset is not None and len(inline_query.offset):
            self.from_ = int(inline_query.offset)

    def set_extra_items(self, value: int):
        if value is None:
            return

        self.extra_items = value

    def get_next_offset(self) -> str:
        return (
            str(self.from_ + len(self.results) - self.extra_items)
            if len(self.results)
            else None
        )

    def answer_query(
        self,
        telegram_inline_query: pyrogram.types.InlineQuery,
    ) -> None:
        """
        Answer the telegram inline query

        Parameters
        ----------
        telegram_inline_query : pyrogram.types.InlineQuery
            Telegram InlineQuery object to answer

        Raises
        ------
        NullTelegramInlineQuery
            When the telegram inline query object is None
        """
        if telegram_inline_query is None:
            raise NullTelegramInlineQuery()
        # if not len(self.results) or self.results is None:
        #     raise Exception("results cannot be empty")
        try:
            telegram_inline_query.answer(
                self.results,
                cache_time=self.cache_time,
                next_offset=self.get_next_offset(),
            )
        except QueryIdInvalid:
            pass
        except BadRequest as e:
            logger.exception(e)
        except Exception as e:
            logger.exception(e)
