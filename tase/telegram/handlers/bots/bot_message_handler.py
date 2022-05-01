import random
import textwrap
import unicodedata
from datetime import timedelta, datetime
from typing import List

import emoji
import pyrogram
from pyrogram.enums import ParseMode

from static.emoji import fruit_list, _search_emoji, _checkmark_emoji, _clock_emoji, _traffic_light, _floppy_emoji
from tase.my_logger import logger
from pyrogram import handlers
from pyrogram import filters

from tase.telegram.handlers import BaseHandler, HandlerMetadata
from tase.utils import get_timestamp


class BotMessageHandler(BaseHandler):

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
                filters=filters.private & filters.regex("dl_"),
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

    def start_bot_handler(self, client: 'pyrogram.Client', message: 'pyrogram.types.Message'):
        logger.debug(f"start_bot_handler: {message.command}")

    def base_commands_handler(self, client: 'pyrogram.Client', message: 'pyrogram.types.Message'):
        logger.debug(f"base_commands_handler: {message.command}")

    def downloads_handler(self, client: 'pyrogram.Client', message: 'pyrogram.types.Message'):
        """
        Check if the message is coming from a Telegram client and contains "dl_" regex, and then submit
        a thread to retrieve the searched audio file
        :param client: Telegram Client
        :param message: Telegram message object
        :return:
        """
        logger.debug(f"base_downloads_handler: {message.text}")
        download_url = message.text.split('/dl_')[1]
        db_audio_doc = self.db.get_audio_doc_by_download_url(download_url)
        if db_audio_doc:
            audio_file_cache = self.db.get_audio_file_from_cache(db_audio_doc, self.telegram_client.telegram_id)
            if not audio_file_cache:
                db_chat = self.db.get_chat_by_chat_id(db_audio_doc.chat_id)
                messages = client.get_messages(db_chat.username, [db_audio_doc.message_id])
                if not messages or not len(messages):
                    # todo: could not get the audio from telegram servers, what to do now?
                    logger.error("could not get the audio from telegram servers, what to do now?")
                    return
                file_id = messages[0].audio.file_id
            else:
                file_id = audio_file_cache.file_id

            message.reply_audio(
                audio=file_id,
                caption=db_audio_doc.message_caption if db_audio_doc.message_caption else "my caption"
            )
        else:
            # todo: An Error occurred while processing this audio download url, why?
            logger.error(f"An Error occurred while processing this audio download url: {download_url}")
            message.reply_text(
                "An Error occurred while processing this audio download url"
            )

    def search_query_handler(self, client: 'pyrogram.Client', message: 'pyrogram.types.Message'):
        logger.info(f"search_query_handler: {message.text}")

        from_user = message.from_user
        chat = message.chat
        message_date = message.date
        query = message.text

        found_any = True
        db_audio_docs = []

        if not query:
            found_any = False
        else:
            db_audio_docs, query_metadata = self.db.search_audio(query, size=10)
            if not db_audio_docs or not len(db_audio_docs) or not len(query_metadata):
                found_any = False

            db_query = self.db.get_or_create_query(
                self.telegram_client.telegram_id,
                from_user,
                query,
                query_date=get_timestamp(message.date),
                query_metadata=query_metadata,
                audio_docs=db_audio_docs,
            )

        if found_any:
            x = len([None for ch in query if unicodedata.bidirectional(ch) in ('R', 'AL')]) / float(len(query))
            dir_str = "&rlm;" if x > 0.5 else '&lrm;'
            fruit = random.choice(fruit_list)

            text = f"<b>{_search_emoji} Search results for: {textwrap.shorten(query, width=100, placeholder='...')}</b>\n"
            text += f"{_checkmark_emoji} Better results are at the bottom of the list\n\n\n"
            _headphone_emoji = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':headphone:']

            for index, db_audio in reversed(list(enumerate(db_audio_docs))):

                duration = timedelta(seconds=db_audio.duration)
                d = datetime(1, 1, 1) + duration
                _performer = db_audio.performer if db_audio.performer else ""
                _title = db_audio.title if db_audio.title else ""
                _file_name = db_audio.file_name if db_audio.file_name else ""
                if not (len(_title) < 2 or len(_performer) < 2):
                    name = f"{_performer} - {_title}"
                elif not len(_performer) < 2:
                    name = f"{_performer} - {_file_name}"
                else:
                    name = _file_name

                text += f"<b>{str(index + 1)}. {dir_str} {_headphone_emoji} {fruit if index == 0 else ''}</b>" \
                        f"<b>{textwrap.shorten(name, width=35, placeholder='...')}</b>\n" \
                        f"{dir_str}     {_floppy_emoji} | {round(db_audio.file_size / 1000_000, 1)} MB  " \
                        f"{dir_str}{_clock_emoji} | {str(d.hour) + ':' if d.hour > 0 else ''}{d.minute}:{d.second}\n{dir_str}" \
                        f"{dir_str}      Download: /dl_{db_audio.download_url}\n" \
                        f"{40 * '-' if index != 0 else ''}{dir_str} \n\n"
        else:
            text = f"{_traffic_light}  No results were found!" \
                   f"\n<pre>{textwrap.shorten(query, width=200, placeholder='...')}</pre>"

        message.reply_text(
            text=text,
            quote=True,
            parse_mode=ParseMode.HTML,
        )

    def bot_message_handler(self, client: 'pyrogram.Client', message: 'pyrogram.types.Message'):
        logger.info(f"bot_message_handler: {message}")
