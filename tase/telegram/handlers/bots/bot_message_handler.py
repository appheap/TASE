import textwrap
from datetime import timedelta, datetime
from typing import List

import pyrogram
from jinja2 import Template
from pyrogram import filters
from pyrogram import handlers
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardMarkup

from tase.db import graph_models
from tase.my_logger import logger
from tase.telegram.handlers import BaseHandler, HandlerMetadata, exception_handler
from tase.telegram.inline_buton_globals import buttons
from tase.telegram.templates import QueryResultsData, NoResultsWereFoundData, AudioCaptionData, ChooseLanguageData, WelcomeData, \
    HelpData
from tase.utils import get_timestamp, _trans, languages_object
from tase.telegram import template_globals


class BotMessageHandler(BaseHandler):
    results_template: Template = None
    no_results_were_found: Template = None

    def init_handlers(self) -> List[HandlerMetadata]:

        handlers_list = [
            HandlerMetadata(
                cls=handlers.MessageHandler,
                callback=self.start_bot_handler,
                filters=filters.command(['start']),
                group=0,
            ),
            HandlerMetadata(
                cls=handlers.MessageHandler,
                callback=self.base_commands_handler,
                filters=filters.command(['lang', 'help', 'home']),
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
                filters=filters.private & filters.text & ~filters.bot & ~filters.via_bot & ~filters.media,
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
    def start_bot_handler(self, client: 'pyrogram.Client', message: 'pyrogram.types.Message'):
        logger.debug(f"start_bot_handler: {message.command}")

        db_from_user = self.db.get_or_create_user(message.from_user)

        self.say_welcome(client, db_from_user, message)

        if db_from_user.chosen_language_code is None:
            self.choose_language(client, db_from_user, message)

    @exception_handler
    def base_commands_handler(self, client: 'pyrogram.Client', message: 'pyrogram.types.Message'):
        logger.debug(f"base_commands_handler: {message.command}")

        db_from_user = self.db.get_or_create_user(message.from_user)

        command = message.command[0]
        if not command or command is None:
            return

        if command == 'lang':
            self.choose_language(client, db_from_user, message)
        elif command == 'help':
            self.show_help(client, db_from_user, message)
        elif command == 'home':
            pass
        else:
            pass

    @exception_handler
    def downloads_handler(self, client: 'pyrogram.Client', message: 'pyrogram.types.Message'):
        """
        Check if the message is coming from a Telegram client and contains "dl_" regex, and then submit
        a thread to retrieve the searched audio file
        :param client: Telegram Client
        :param message: Telegram message object
        :return:
        """
        logger.debug(f"base_downloads_handler: {message.text}")

        # todo: find a better way to update user when it's necessary
        db_user = self.db.get_user_by_user_id(message.from_user.id)
        if not db_user:
            db_user = self.db.update_or_create_user(message.from_user)

        # todo: handle errors for invalid messages
        download_url = message.text.split('/dl_')[1]
        db_hit = self.db.get_hit_by_download_url(download_url)
        db_audio = self.db.get_audio_from_hit(db_hit)
        db_audio_doc = self.db.get_audio_doc_by_key(db_audio.key)
        if db_audio_doc:
            audio_file_cache = self.db.get_audio_file_from_cache(db_audio_doc, self.telegram_client.telegram_id)
            db_chat = self.db.get_chat_by_chat_id(db_audio_doc.chat_id)
            if not audio_file_cache:
                messages = client.get_messages(db_chat.username, [db_audio_doc.message_id])
                if not messages or not len(messages):
                    # todo: could not get the audio from telegram servers, what to do now?
                    logger.error("could not get the audio from telegram servers, what to do now?")
                    return
                file_id = messages[0].audio.file_id
            else:
                file_id = audio_file_cache.file_id

            text = template_globals.audio_caption_template.render(
                AudioCaptionData.parse_from_audio_doc(
                    db_audio_doc,
                    db_user,
                    db_chat,
                    bot_url='https://t.me/bot?start',
                    include_source=True,
                )
            )

            message.reply_audio(
                audio=file_id,
                caption=text,
                parse_mode=ParseMode.HTML,
            )

            db_download = self.db.get_or_create_download_from_download_url(
                download_url, db_user,
                self.telegram_client.telegram_id,
            )
        else:
            # todo: An Error occurred while processing this audio download url, why?
            logger.error(f"An Error occurred while processing this audio download url: {download_url}")
            message.reply_text(
                _trans("An Error occurred while processing this audio download url", db_user.chosen_language_code)
            )

    @exception_handler
    def search_query_handler(self, client: 'pyrogram.Client', message: 'pyrogram.types.Message'):
        logger.info(f"search_query_handler: {message.text}")
        # todo: fix this
        lang_code = message.from_user.language_code

        from_user = message.from_user
        chat = message.chat
        message_date = message.date
        query = message.text

        # update the user
        db_from_user = self.db.update_or_create_user(message.from_user)

        # todo: fix this
        db_from_user = self.db.get_user_by_user_id(message.from_user.id)

        found_any = True
        db_audio_docs = []

        if not query:
            found_any = False
        else:
            db_audio_docs, query_metadata = self.db.search_audio(query, size=10)
            if not db_audio_docs or not len(db_audio_docs) or not len(query_metadata):
                found_any = False

            db_query, db_hits = self.db.get_or_create_query(
                self.telegram_client.telegram_id,
                from_user,
                query,
                query_date=get_timestamp(message.date),
                query_metadata=query_metadata,
                audio_docs=db_audio_docs,
            )

        if found_any:
            def process_item(index, db_audio, db_hit):
                duration = timedelta(seconds=db_audio.duration)
                d = datetime(1, 1, 1) + duration
                _performer = db_audio.performer or ""
                _title = db_audio.title or ""
                _file_name = db_audio.file_name or ""
                if not (len(_title) < 2 or len(_performer) < 2):
                    name = f"{_performer} - {_title}"
                elif not len(_performer) < 2:
                    name = f"{_performer} - {_file_name}"
                else:
                    name = _file_name

                return {
                    'index': f"{index + 1:02}",
                    'name': textwrap.shorten(name, width=35, placeholder='...'),
                    'file_size': round(db_audio.file_size / 1000_000, 1),
                    'time': f"{str(d.hour) + ':' if d.hour > 0 else ''}{d.minute:02}:{d.second:02}",
                    'url': db_hit.download_url,
                    'sep': f"{40 * '-' if index != 0 else ''}",
                }

            items = [
                process_item(index, db_audio, db_hit)
                for index, (db_audio, db_hit) in reversed(list(enumerate(zip(db_audio_docs, db_hits))))
            ]

            data = QueryResultsData(
                query=query,
                items=items,
                lang_code=db_from_user.chosen_language_code,
            )

            text = template_globals.query_results_template.render(data)
        else:
            text = template_globals.no_results_were_found_template.render(
                NoResultsWereFoundData(
                    query=query,
                    lang_code=db_from_user.chosen_language_code,
                )
            )

        message.reply_text(
            text=text,
            quote=True,
            parse_mode=ParseMode.HTML,
        )

    @exception_handler
    def bot_message_handler(self, client: 'pyrogram.Client', message: 'pyrogram.types.Message'):
        logger.info(f"bot_message_handler: {message}")

    #######################################################################################################

    def say_welcome(
            self,
            client: 'pyrogram.Client',
            db_from_user: graph_models.vertices.User,
            message: 'pyrogram.types.Message'
    ) -> None:
        """
        Shows a welcome message to the user after hitting 'start'

        :param client: Telegram client
        :param db_from_user: User Object from the graph database
        :param message: Telegram message object
        :return:
        """
        data = WelcomeData(
            name=message.from_user.first_name or message.from_user.last_name,
            lang_code=db_from_user.chosen_language_code,
        )

        client.send_message(
            chat_id=message.from_user.id,
            text=template_globals.welcome_template.render(data),
            parse_mode=ParseMode.HTML
        )

    def show_help(
            self,
            client: 'pyrogram.Client',
            db_from_user: graph_models.vertices.User,
            message: 'pyrogram.types.Message'
    ) -> None:
        """
        Shows the help menu

        :param client: Telegram client
        :param db_from_user: User Object from the graph database
        :param message: Telegram message object
        :return:
        """
        data = HelpData(
            support_channel_username='support_channel_username',
            url1='https://github.com',
            url2='https://github.com',
            lang_code=db_from_user.chosen_language_code,
        )

        markup = [
            [
                buttons['download_history'].get_inline_keyboard_button(),
                buttons['my_playlists'].get_inline_keyboard_button(),
            ],
            [
                buttons['back'].get_inline_keyboard_button(),
            ],
            [
                buttons['advertisement'].get_inline_keyboard_button(),
                buttons['help_catalog'].get_inline_keyboard_button(),
            ]
        ]
        markup = InlineKeyboardMarkup(markup)

        client.send_message(
            chat_id=message.from_user.id,
            text=template_globals.help_template.render(data),
            parse_mode=ParseMode.HTML,
            reply_markup=markup,
        )

    def choose_language(
            self,
            client: 'pyrogram.Client',
            db_from_user: graph_models.vertices.User,
            message: 'pyrogram.types.Message'
    ) -> None:
        """
        Ask users to choose a language among a menu shows a list of available languages.

        :param client: Telegram client
        :param db_from_user: User Object from the graph database
        :param message: Telegram message object
        :return:
        """
        data = ChooseLanguageData(
            name=message.from_user.first_name or message.from_user.last_name,
            lang_code=db_from_user.chosen_language_code,
        )

        client.send_message(
            chat_id=message.from_user.id,
            text=template_globals.choose_language_template.render(data),
            reply_markup=languages_object.get_choose_language_markup(),
            parse_mode=ParseMode.HTML
        )
