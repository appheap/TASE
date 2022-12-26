import random
from typing import List

import pyrogram
from jinja2 import Template
from pyrogram import filters, handlers
from pyrogram.enums import ParseMode

from tase.common.bot_tasks_checker import BotTaskChecker
from tase.common.preprocessing import telegram_url_regex, url_regex, clean_text, find_telegram_usernames
from tase.common.utils import (
    datetime_to_timestamp,
    emoji,
    async_exception_handler,
    async_timed,
)
from tase.my_logger import logger
from tase.telegram.bots.bot_commands import BaseCommand, BotCommandType
from tase.telegram.bots.ui.templates import (
    BaseTemplate,
    NoResultsWereFoundData,
    QueryResultsData,
)
from tase.telegram.update_handlers.base import BaseHandler, HandlerMetadata


class BotMessageHandler(BaseHandler):
    results_template: Template = None
    no_results_were_found: Template = None

    def init_handlers(self) -> List[HandlerMetadata]:

        handlers_list = [
            HandlerMetadata(
                cls=handlers.MessageHandler,
                callback=self.commands_handler,
                filters=filters.command(BaseCommand.get_all_valid_commands()),
                group=0,
            ),
            HandlerMetadata(
                cls=handlers.MessageHandler,
                callback=self.downloads_handler,
                filters=filters.private & filters.regex("^/dl_[a-zA-Z0-9_]+$"),
                group=0,
            ),
            HandlerMetadata(
                cls=handlers.MessageHandler,
                callback=self.search_query_handler,
                filters=filters.private
                & ~filters.forwarded
                & filters.text
                & ~filters.bot
                & ~filters.via_bot
                & ~filters.media
                & ~filters.regex(telegram_url_regex)
                & ~filters.regex(url_regex)
                & ~filters.regex("^(.*/+.*)+$"),
                group=0,
            ),
            HandlerMetadata(
                cls=handlers.MessageHandler,
                callback=self.bot_message_handler,
                group=0,
            ),
        ]
        return handlers_list

    @async_exception_handler()
    @async_timed()
    async def commands_handler(
        self,
        client: pyrogram.Client,
        message: pyrogram.types.Message,
    ):
        logger.debug(f"commands_handler: {message.command}")

        await BaseCommand.run_command(client, message, self)

    @async_exception_handler()
    @async_timed()
    async def downloads_handler(
        self,
        client: pyrogram.Client,
        message: pyrogram.types.Message,
    ):
        """
        Check if the message is coming from a Telegram client and contains "dl_" regex, and then submit
        a thread to retrieve the searched audio file

        Parameters
        ----------
        client : pyrogram.Client
            Client receiving this update
        message : pyrogram.types.Message
            Message associated with update
        """
        logger.debug(f"base_downloads_handler: {message.text}")

        from_user = await self.db.graph.get_interacted_user(message.from_user)
        await self.download_audio(
            client,
            from_user,
            message.text,
            message,
        )

    @async_exception_handler()
    @async_timed()
    async def search_query_handler(
        self,
        client: pyrogram.Client,
        message: pyrogram.types.Message,
    ):
        logger.info(f"search_query_handler: {message.text}")
        query = message.text

        from_user = await self.db.graph.get_interacted_user(message.from_user)

        if from_user.chosen_language_code is None or not len(from_user.chosen_language_code):
            await BaseCommand.run_command(client, message, self, BotCommandType.LANGUAGE)
            return

        # check if this message is reply to any bot task
        if await BotTaskChecker.check(
            self.db,
            await self.db.document.get_latest_bot_task(
                from_user.user_id,
                self.telegram_client.telegram_id,
            ),
            from_user,
            message,
        ):
            return

        es_audio_docs = None
        query_metadata = None
        if not query:
            found_any = False
        else:
            if len(query) <= 2:
                found_any = False
            else:
                es_audio_docs, query_metadata = await self.db.index.search_audio(
                    clean_text(query),
                    size=10,
                    filter_by_valid_for_inline_search=False,  # todo: is this a good idea?
                )
                if es_audio_docs and query_metadata:
                    hit_download_urls = await self.db.graph.generate_hit_download_urls(size=10)
                    found_any = True
                else:
                    found_any = False

        if found_any:
            data = QueryResultsData.parse_from_query(
                query=query,
                lang_code=from_user.chosen_language_code,
                es_audio_docs=es_audio_docs,
                hit_download_urls=hit_download_urls,
            )

            text = BaseTemplate.registry.query_results_template.render(data)
        else:
            text = BaseTemplate.registry.no_results_were_found_template.render(
                NoResultsWereFoundData(
                    query=query,
                    lang_code=from_user.chosen_language_code,
                )
            )

        from tase.telegram.bots.ui.inline_buttons.common import get_more_results_markup_keyboad

        await message.reply_text(
            text=text,
            quote=True,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
            reply_markup=get_more_results_markup_keyboad(
                from_user.chosen_language_code,
                query,
            )
            if found_any
            else None,
        )

        if found_any and es_audio_docs:
            audio_vertices = await self.db.graph.get_audios_from_keys([doc.id for doc in es_audio_docs])
            search_metadata_lst = [es_audio_doc.search_metadata for es_audio_doc in es_audio_docs]
        else:
            audio_vertices = None
            search_metadata_lst = None
            query_metadata = None

        await self.db.graph.get_or_create_query(
            self.telegram_client.telegram_id,
            from_user,
            query,
            datetime_to_timestamp(message.date),
            audio_vertices,
            query_metadata,
            search_metadata_lst,
            hit_download_urls=hit_download_urls,
        )

    @async_exception_handler()
    async def bot_message_handler(
        self,
        client: "pyrogram.Client",
        message: "pyrogram.types.Message",
    ):
        # logger.info(f"bot_message_handler: {message}")

        if not message.from_user:
            # message is not from a user
            # message is coming from a chat
            await self.update_audio_doc_coming_in_from_archive_channel(message)
            return

        from_user = await self.db.graph.get_interacted_user(message.from_user, update=True)

        if message.via_bot and message.via_bot.id == self.telegram_client.telegram_id:
            # messages that are from this bot are not considered as a contribution
            return

        if message.from_user.is_bot or message.from_user.is_fake or message.from_user.is_scam or message.from_user.is_restricted:
            return

        texts_to_check = set()

        texts_to_check.add(message.caption)
        texts_to_check.add(message.text)

        if message.entities:
            for entity in message.entities:
                texts_to_check.add(entity.url)

        if message.media:
            if message.caption_entities:
                for entity in message.caption_entities:
                    texts_to_check.add(entity.url)

            if message.audio:
                texts_to_check.add(message.audio.title)
                texts_to_check.add(message.audio.performer)
                texts_to_check.add(message.audio.file_name)
            elif message.document:
                texts_to_check.add(message.document.file_name)
            elif message.video:
                texts_to_check.add(message.video.file_name)
            else:
                pass

        if message.forward_from_chat:
            await self.db.graph.update_or_create_chat(message.forward_from_chat)

            if message.forward_from_chat.username:
                texts_to_check.add(f"@{message.forward_from_chat.username}")
            texts_to_check.add(message.forward_from_chat.description)

        if message.reply_markup and message.reply_markup.inline_keyboard:
            for inline_keyboard_button_lst in message.reply_markup.inline_keyboard:
                for inline_keyboard_button in inline_keyboard_button_lst:
                    texts_to_check.add(inline_keyboard_button.text)
                    texts_to_check.add(inline_keyboard_button.url)

        texts_to_check = {item.lower() for item in filter(lambda item: item is not None and len(item), texts_to_check)}
        texts_to_check = " ".join(texts_to_check)

        found_any = False

        for username in find_telegram_usernames(texts_to_check, return_start_index=False):
            logger.debug(f"username `{username}` was found")
            username_vertex = await self.db.graph.get_or_create_username(
                username,
                create_mention_edge=False,
            )
            if username_vertex and not found_any:
                found_any = True

        if not found_any:
            logger.debug("No usernames found in this message")
        else:
            # fixme: translate this string
            await message.reply_text(
                f"Special thanks for your contribution <b>{message.from_user.first_name or message.from_user.last_name}</b>. {random.choice(emoji.plants_list)}{random.choice(emoji.heart_list)}"
            )

        if message.forward_from:
            await self.db.graph.update_or_create_user(message.forward_from)

    #######################################################################################################
