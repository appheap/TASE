import random
from typing import List

import pyrogram
from jinja2 import Template
from pyrogram import filters, handlers
from pyrogram.enums import ParseMode

from tase.common.bot_tasks_checker import BotTaskChecker
from tase.common.preprocessing import telegram_url_regex, url_regex
from tase.common.utils import (
    datetime_to_timestamp,
    exception_handler,
    find_telegram_usernames,
    emoji,
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

    @exception_handler
    def commands_handler(
        self,
        client: pyrogram.Client,
        message: pyrogram.types.Message,
    ):
        logger.debug(f"commands_handler: {message.command}")

        BaseCommand.run_command(client, message, self)

    @exception_handler
    def downloads_handler(
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

        from_user = self.db.graph.get_interacted_user(message.from_user)
        self.download_audio(
            client,
            from_user,
            message.text,
            message,
        )

    @exception_handler
    def search_query_handler(
        self,
        client: pyrogram.Client,
        message: pyrogram.types.Message,
    ):
        logger.info(f"search_query_handler: {message.text}")
        query = message.text

        from_user = self.db.graph.get_interacted_user(message.from_user)

        if from_user.chosen_language_code is None or not len(
            from_user.chosen_language_code
        ):
            BaseCommand.run_command(client, message, self, BotCommandType.LANGUAGE)
            return

        # check if this message is reply to any bot task
        if BotTaskChecker.check(
            self.db,
            self.db.document.get_latest_bot_task(
                from_user.user_id,
                self.telegram_client.telegram_id,
            ),
            from_user,
            message,
        ):
            return

        found_any = True
        if not query:
            found_any = False
        else:
            if len(query) <= 2:
                found_any = False
            else:
                es_audio_docs, query_metadata = self.db.index.search_audio(
                    query,
                    size=10,
                    filter_by_valid_for_inline_search=False,  # todo: is this a good idea?
                )
                if (
                    not es_audio_docs
                    or not len(es_audio_docs)
                    or query_metadata is None
                ):
                    found_any = False

                audio_vertices = list(
                    self.db.graph.get_audios_from_keys(
                        [doc.id for doc in es_audio_docs]
                    )
                )
                search_metadata_lst = [
                    es_audio_doc.search_metadata for es_audio_doc in es_audio_docs
                ]

                db_query, hits = self.db.graph.get_or_create_query(
                    self.telegram_client.telegram_id,
                    from_user,
                    query,
                    datetime_to_timestamp(message.date),
                    audio_vertices,
                    query_metadata,
                    search_metadata_lst,
                )
                if db_query and hits:
                    found_any = True
                else:
                    found_any = False

        if found_any:
            data = QueryResultsData.parse_from_query(
                query=query,
                lang_code=from_user.chosen_language_code,
                es_audio_docs=es_audio_docs,
                hits=hits,
            )

            text = BaseTemplate.registry.query_results_template.render(data)
        else:
            text = BaseTemplate.registry.no_results_were_found_template.render(
                NoResultsWereFoundData(
                    query=query,
                    lang_code=from_user.chosen_language_code,
                )
            )

        message.reply_text(
            text=text,
            quote=True,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )

    @exception_handler
    def bot_message_handler(
        self,
        client: "pyrogram.Client",
        message: "pyrogram.types.Message",
    ):
        # logger.info(f"bot_message_handler: {message}")

        from_user = self.db.graph.get_interacted_user(message.from_user, update=True)

        if message.via_bot and message.via_bot.id == self.telegram_client.telegram_id:
            # messages that are from this bot are not considered as a contribution
            return

        if (
            message.from_user.is_bot
            or message.from_user.is_fake
            or message.from_user.is_scam
            or message.from_user.is_restricted
        ):
            return

        # fixme: translate this string
        message.reply_text(
            f"Special thanks for your contribution <b>{message.from_user.first_name or message.from_user.last_name}</b>. {random.choice(emoji.plants_list)}{random.choice(emoji.heart_list)}"
        )

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
            self.db.graph.update_or_create_chat(message.forward_from_chat)

            if message.forward_from_chat.username:
                texts_to_check.add(f"@{message.forward_from_chat.username}")
            texts_to_check.add(message.forward_from_chat.description)

        if message.reply_markup and message.reply_markup.inline_keyboard:
            for inline_keyboard_button_lst in message.reply_markup.inline_keyboard:
                for inline_keyboard_button in inline_keyboard_button_lst:
                    texts_to_check.add(inline_keyboard_button.text)
                    texts_to_check.add(inline_keyboard_button.url)

        texts_to_check = {
            item.lower()
            for item in filter(lambda item: item is not None, texts_to_check)
        }

        found_any = False

        for text in texts_to_check:
            if text is None or not len(text):
                continue

            for username, idx in find_telegram_usernames(text):
                logger.debug(f"username `{username}` was found")
                username_vertex = self.db.graph.get_or_create_username(
                    username,
                    create_mention_edge=False,
                )
                if username_vertex and not found_any:
                    found_any = True

        if not found_any:
            logger.debug("No usernames found in this message")

        if message.forward_from:
            self.db.graph.update_or_create_user(message.forward_from)

    #######################################################################################################
