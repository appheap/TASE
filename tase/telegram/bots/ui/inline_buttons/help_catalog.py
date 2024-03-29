from typing import Optional, List

import pyrogram
from pyrogram.enums import ParseMode
from pyrogram.types import InlineQueryResultArticle, InputTextMessageContent

from tase.common.utils import _trans, emoji
from tase.db.arangodb import graph as graph_models
from tase.telegram.bots.inline import CustomInlineQueryResult
from tase.telegram.bots.ui.base import InlineButton, InlineButtonType, ButtonActionType, InlineButtonData
from tase.telegram.update_handlers.base import BaseHandler


class HelpCatalogButtonData(InlineButtonData):
    __button_type__ = InlineButtonType.HELP_CATALOG

    @classmethod
    def generate_data(cls, inline_command: str) -> Optional[str]:
        return f"${inline_command}"

    @classmethod
    def __parse__(
        cls,
        data_split_lst: List[str],
    ) -> Optional[InlineButtonData]:
        return HelpCatalogButtonData()


class HelpCatalogInlineButton(InlineButton):
    __type__ = InlineButtonType.HELP_CATALOG
    action = ButtonActionType.CURRENT_CHAT_INLINE
    __switch_inline_query__ = "help_catalog"

    s_help = _trans("Help")
    text = f"{s_help} | {emoji._exclamation_question_mark}"

    @classmethod
    def get_keyboard(
        cls,
        *,
        lang_code: Optional[str] = "en",
    ) -> pyrogram.types.InlineKeyboardButton:
        return cls.get_button(cls.__type__).__parse_keyboard_button__(
            switch_inline_query_current_chat=HelpCatalogButtonData.generate_data(cls.switch_inline_query()),
            lang_code=lang_code,
        )

    async def on_inline_query(
        self,
        handler: BaseHandler,
        result: CustomInlineQueryResult,
        from_user: graph_models.vertices.User,
        client: pyrogram.Client,
        telegram_inline_query: pyrogram.types.InlineQuery,
        query_date: int,
        inline_button_data: Optional[HelpCatalogButtonData] = None,
    ):
        if not result.is_first_page():
            # do not populate result if it is not the first page.
            return

        # todo: make these messages translatable
        results = [
            InlineQueryResultArticle(
                id="1",
                title="TASE Developers",
                description="To see authors's github and social media, click here",
                thumb_url="https://telegra.ph/file/d15b185d0154fc8a92210.jpg",
                input_message_content=InputTextMessageContent(
                    f"Everything you need to know before promoting your business: \n"
                    f"<a href='https://github.com/appheap/TASE/'>"
                    f"<b>Telegram Audio Search Engine Advertising</b></a>",
                    parse_mode=ParseMode.HTML,
                ),
            ),
            InlineQueryResultArticle(
                id="2",
                title="1. How To Advertise?",
                description="If you need advertising, click here",
                thumb_url="https://telegra.ph/file/d15b185d0154fc8a92210.jpg",
                input_message_content=InputTextMessageContent(
                    f"Everything you need to know before promoting your business: \n"
                    f"<a href='https://github.com/appheap/TASE/'>"
                    f"<b>Telegram Audio Search Engine Advertising</b></a>",
                    parse_mode=ParseMode.HTML,
                ),
            ),
            InlineQueryResultArticle(
                id="3",
                title="2. How To Search For And Download An Audio Track",
                description="You can easily send your audio file and get indexed by Telegram Audio Search Engine bot",
                thumb_url="https://telegra.ph/file/d15b185d0154fc8a92210.jpg",
                input_message_content=InputTextMessageContent(
                    f"Read searching tutorial on this page: \n<a href='https://github.com/appheap/TASE/'><b>Optimal Search</b></a>",
                    parse_mode=ParseMode.HTML,
                ),
            ),
            InlineQueryResultArticle(
                id="4",
                title="3. How to Register My Own Audio Track?",
                description="You can simply send your audio file and have it indexed by Telegram audio search engin",
                thumb_url="https://telegra.ph/file/d15b185d0154fc8a92210.jpg",
                input_message_content=InputTextMessageContent(
                    f"Here is a complete guide on "
                    f"<a href='https://github.com/appheap/TASE/'>"
                    f"<b>how to add my audio track</b></a> (music, podcast, etc.)"
                    f" to be shown in the results",
                    parse_mode=ParseMode.HTML,
                ),
            ),
            InlineQueryResultArticle(
                id="5",
                title="4. How To Add My Channel To Telegram Audio Search Engine",
                description="If you feel your channel has not been indexed",
                thumb_url="https://telegra.ph/file/d15b185d0154fc8a92210.jpg",
                input_message_content=InputTextMessageContent(
                    f"Here is a complete guide on "
                    f"<a href='https://github.com/appheap/TASE/'>"
                    f"<b>how to add my channel</b></a> to be shown by Telegram Audio Search Engine",
                    parse_mode=ParseMode.HTML,
                ),
            ),
            InlineQueryResultArticle(
                id="6",
                title="5. Contact Us",
                description="If you need to contact Telegram audio search engin admins then hit this item",
                thumb_url="https://telegra.ph/file/d15b185d0154fc8a92210.jpg",
                input_message_content=InputTextMessageContent(
                    f"you can be in touch with us through @{'admin_username'}\n"
                    f"For further information please read "
                    f"<a href='https://github.com/appheap/TASE/'>Contact Telegram Audio Search Engine</a>",
                    parse_mode=ParseMode.HTML,
                ),
            ),
            InlineQueryResultArticle(
                id="7",
                title="6. About Us",
                description="If you like to find out more about us, click on this link",
                thumb_url="https://telegra.ph/file/d15b185d0154fc8a92210.jpg",
                input_message_content=InputTextMessageContent(
                    f"<b>Read more about us on the following page:\n<a href='https://github.com/appheap/TASE/'>About Telegram Audio Search Engine</a></b>",
                    parse_mode=ParseMode.HTML,
                ),
            ),
        ]

        result.set_results(
            results,
            count=True,
        )
        result.cache_time = 300  # todo: fix me

        await result.answer_query()
