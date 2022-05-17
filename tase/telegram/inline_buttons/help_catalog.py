from typing import Match

import pyrogram
from pyrogram.enums import ParseMode
from pyrogram.types import InlineQueryResultArticle, InputTextMessageContent

from .inline_button import InlineButton
from ..telegram_client import TelegramClient
# from ..handlers import BaseHandler
from ...db import DatabaseClient, graph_models
from ...utils import emoji, _trans


class HelpCatalogInlineButton(InlineButton):
    name = "help_catalog"

    s_help = _trans("Help")
    text = f"{s_help} | {emoji._exclamation_question_mark}"

    switch_inline_query_current_chat = f"#help_catalog"

    def on_inline_query(
            self,
            client: 'pyrogram.Client',
            inline_query: 'pyrogram.types.InlineQuery',
            handler: 'BaseHandler',
            db: 'DatabaseClient',
            telegram_client: 'TelegramClient',
            db_from_user: graph_models.vertices.User,
            reg: Match,
    ):
        # todo: make these messages translatable
        results = [
            InlineQueryResultArticle(
                title="TASE Developers",
                description="To see authors's github and social media, click here",
                thumb_url="https://telegra.ph/file/d15b185d0154fc8a92210.jpg",
                input_message_content=InputTextMessageContent(
                    f"Everything you need to know before promoting your business: \n"
                    f"<a href='https://github.com/appheap/TASE/'>"
                    f"<b>Telegram Audio Search Engine Advertising</b></a>",
                    parse_mode=ParseMode.HTML
                ),
            ), InlineQueryResultArticle(
                title="1. How To Advertise?",
                description="If you need advertising, click here",
                thumb_url="https://telegra.ph/file/d15b185d0154fc8a92210.jpg",
                input_message_content=InputTextMessageContent(
                    f"Everything you need to know before promoting your business: \n"
                    f"<a href='https://github.com/appheap/TASE/'>"
                    f"<b>Telegram Audio Search Engine Advertising</b></a>",
                    parse_mode=ParseMode.HTML
                )
            ), InlineQueryResultArticle(
                title="2. How To Search For And Download An Audio Track",
                description="You can easily send your audio file and get indexed by Telegram Audio Search Engine bot",
                thumb_url="https://telegra.ph/file/d15b185d0154fc8a92210.jpg",
                input_message_content=InputTextMessageContent(
                    f"Read searching tutorial on this page: \n"
                    f"<a href='https://github.com/appheap/TASE/'>"
                    f"<b>Optimal Search</b></a>",
                    parse_mode=ParseMode.HTML
                )
            ), InlineQueryResultArticle(
                title="3. How to Register My Own Audio Track?",
                description="You can simply send your audio file and have it indexed by Telegram audio search engin",
                thumb_url="https://telegra.ph/file/d15b185d0154fc8a92210.jpg",
                input_message_content=InputTextMessageContent(
                    f"Here is a complete guide on "
                    f"<a href='https://github.com/appheap/TASE/'>"
                    f"<b>how to add my audio track</b></a> (music, podcast, etc.)"
                    f" to be shown in the results", parse_mode=ParseMode.HTML
                )
            ), InlineQueryResultArticle(
                title="4. How To Add My Channel To Telegram Audio Search Engine",
                description="If you feel your channel has not been indexed",
                thumb_url="https://telegra.ph/file/d15b185d0154fc8a92210.jpg",
                input_message_content=InputTextMessageContent(
                    f"Here is a complete guide on "
                    f"<a href='https://github.com/appheap/TASE/'>"
                    f"<b>how to add my channel</b></a> to be shown by Telegram Audio Search Engine",
                    parse_mode=ParseMode.HTML
                )
            ), InlineQueryResultArticle(
                title="5. Contact Us",
                description="If you need to contact Telegram audio search engin admins then hit this item",
                thumb_url="https://telegra.ph/file/d15b185d0154fc8a92210.jpg",
                input_message_content=InputTextMessageContent(
                    f"you can be in touch with us through @{'admin_username'}\n"
                    f"For further information please read "
                    f"<a href='https://github.com/appheap/TASE/'>Contact Telegram Audio Search Engine</a>",
                    parse_mode=ParseMode.HTML
                )
            ), InlineQueryResultArticle(
                title="6. About Us",
                description="If you like to find out more about us, click on this link",
                thumb_url="https://telegra.ph/file/d15b185d0154fc8a92210.jpg",
                input_message_content=InputTextMessageContent(
                    f"<b>Read more about us on the following page:\n<a href='https://github.com/appheap/TASE/'>About Telegram Audio Search Engine</a></b>",
                    parse_mode=ParseMode.HTML
                )
            )
        ]

        inline_query.answer(
            results,
            cache_time=10,  # todo: fix me
        )
