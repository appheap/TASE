import collections
from typing import Any, List, Optional, Deque, Iterable

import pyrogram
from pydantic import BaseModel, Field
from pyrogram.errors import QueryIdInvalid, BadRequest

from tase.my_logger import logger


class CustomInlineQueryResult(BaseModel):
    results: Deque[pyrogram.types.InlineQueryResult] = Field(default_factory=collections.deque)
    cache_time: int = Field(default=1)
    from_: int = Field(default=0)
    last_result_total_item_count: int = Field(default=0)
    countable_items_length: int = Field(default=0)

    telegram_inline_query: Optional[pyrogram.types.InlineQuery]

    class Config:
        arbitrary_types_allowed = True

    def __init__(
        self,
        inline_query: pyrogram.types.InlineQuery,
        **data: Any,
    ):
        super().__init__(**data)

        self.telegram_inline_query = inline_query

        if inline_query is None:
            self.from_ = 0
            self.last_result_total_item_count = 0

        if inline_query.offset:
            last_result_len, last_countable_items_len = inline_query.offset.split(":")

            self.from_ = int(last_countable_items_len)
            self.last_result_total_item_count = int(last_result_len)
        else:
            self.from_ = 0
            self.last_result_total_item_count = 0

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

    def get_next_offset(
        self,
        only_countable: bool = False,
    ) -> str:
        return f"{self.from_ + self.countable_items_length if only_countable else len(self.results)}:{self.from_ + self.countable_items_length}"

    def is_first_page(self) -> bool:
        return self.from_ == 0 and self.last_result_total_item_count == 0

    def set_results(
        self,
        results: List[pyrogram.types.InlineQueryResult],
        count: bool = False,
    ) -> None:
        self.results.clear()
        self.results.extend(results)

        if count:
            self.countable_items_length += len(self.results)

    def extend_results(
        self,
        results: Iterable[pyrogram.types.InlineQueryResult],
        count: bool = True,
    ) -> None:
        self.results.extend(results)

        if count:
            self.countable_items_length += len(self.results)

    async def answer_query(
        self,
    ) -> None:
        """
        Answer the telegram inline query

        Raises
        ------
        NullTelegramInlineQuery
            When the telegram inline query object is None
        """
        if self.telegram_inline_query is None or not len(self.results):
            # raise NullTelegramInlineQuery()
            return
        # if not len(self.results) or self.results is None:
        #     raise Exception("results cannot be empty")
        try:
            await self.telegram_inline_query.answer(
                list(self.results),
                cache_time=self.cache_time,
                next_offset=self.get_next_offset(),
                is_personal=True,
            )
        except QueryIdInvalid:
            pass
        except BadRequest as e:
            logger.exception(e)
        except Exception as e:
            logger.exception(e)
