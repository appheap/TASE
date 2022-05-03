import textwrap
import unicodedata
from datetime import timedelta, datetime
from typing import List

import pyrogram
from jinja2 import Template
from pyrogram import filters
from pyrogram import handlers
from pyrogram.enums import ParseMode

from static.emoji import _search_emoji, _checkmark_emoji, _clock_emoji, _traffic_light, _floppy_emoji, _headphone
from tase.my_logger import logger
from tase.telegram.handlers import BaseHandler, HandlerMetadata
from tase.utils import get_timestamp, _trans

_results_template = "<b>{{_search_emoji}} {{search_results_for}} {{query}}</b>{{new_line}}" \
                    "{{_checkmark_emoji}} {{better_results}}{{new_line}}{{new_line}}{{new_line}}" \
                    "{% for item in items%}" \
                    "<b>{{item.index}}. {{d}}{{_headphone_emoji}} </b><b>{{item.name}}</b> {{new_line}}" \
                    "{{d}}      {{_floppy_emoji}} | {{item.file_size}} {{MB}} {{d}}{{_clock_emoji}} | {{item.time}}{{d}}{{new_line}}" \
                    "{{d}}       {{download}} /dl_{{item.url}}{{new_line}}" \
                    "{{item.sep}}{{d}}{{new_line}}{{new_line}}" \
                    "{% endfor %}"

_no_results_were_found_template = "{{_traffic_light}}  {{no_results_were_found}}{{new_line}}<pre>{{query}}</pre>"


class BotMessageHandler(BaseHandler):
    results_template: Template = None
    no_results_were_found: Template = None

    def init_handlers(self) -> List[HandlerMetadata]:
        self.results_template = Template(source=_results_template)
        self.no_results_were_found = Template(source=_no_results_were_found_template)

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
        # todo: fix this
        lang_code = message.from_user.language_code

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

            def process_item(index, db_audio):
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
                    'url': db_audio.download_url,
                    'sep': f"{40 * '-' if index != 0 else ''}",
                }

            items = [
                process_item(index, db_audio)
                for index, db_audio in reversed(list(enumerate(db_audio_docs)))
            ]
            template_data = {
                'query': query,
                'items': items,

                '_search_emoji': _search_emoji,
                '_checkmark_emoji': _checkmark_emoji,
                '_headphone_emoji': _headphone,
                '_floppy_emoji': _floppy_emoji,
                '_clock_emoji': _clock_emoji,

                'd': dir_str,
                'new_line': "\n",
                'MB': _trans('MB', lang_code),

                'download': _trans("Download:", lang_code),
                'better_results': _trans("Better results are at the bottom of the list", lang_code),
                'search_results_for': _trans('Search results for:', lang_code),
            }

            text = self.results_template.render(template_data)

        else:
            template_date = {
                'new_line': "\n",
                '_traffic_light': _traffic_light,

                'no_results_were_found': _trans("No results were found for this query!", lang_code),

                'query': query,
            }
            text = self.no_results_were_found.render(template_date)

        message.reply_text(
            text=text,
            quote=True,
            parse_mode=ParseMode.HTML,
        )

    def bot_message_handler(self, client: 'pyrogram.Client', message: 'pyrogram.types.Message'):
        logger.info(f"bot_message_handler: {message}")
