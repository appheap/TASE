from typing import Any, List

import pyrogram
from pydantic import BaseModel, Field
from pyrogram.errors import QueryIdInvalid, BadRequest

from tase.errors import NullTelegramInlineQuery
from tase.my_logger import logger


class CustomInlineQueryResult(BaseModel):
    results: List[pyrogram.types.InlineQueryResult] = Field(default_factory=list)
    cache_time: int = Field(default=1)
    from_: int = Field(default=0)
    last_result_total_item_count: int = Field(default=0)
    countable_items_length: int = Field(default=0)

    class Config:
        arbitrary_types_allowed = True

    def __init__(
        self,
        inline_query: pyrogram.types.InlineQuery,
        **data: Any,
    ):
        super().__init__(**data)

        if inline_query is None:
            self.from_ = 0

        if inline_query.offset is not None and len(inline_query.offset):
            last_result_len, last_countable_items_len = inline_query.offset.split(":")

            self.from_ = int(last_countable_items_len)
            self.last_result_total_item_count = int(last_result_len)

    def __len__(self):
        return self.countable_items_length

    def add_item(
        self,
        item: pyrogram.types.InlineQueryResult,
        count: bool = True,
    ) -> None:
        self.results.append(item)

        if count:
            self.countable_items_length += 1

    def get_next_offset(self) -> str:
        return f"{len(self.results)}:{self.from_ + self.countable_items_length}"

    def is_first_page(self) -> bool:
        return self.last_result_total_item_count == 0

    def set_results(
        self,
        results: List[pyrogram.types.InlineQueryResult],
        count: bool = False,
    ) -> None:
        self.results = results

        if count:
            self.countable_items_length += len(self.results)

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
