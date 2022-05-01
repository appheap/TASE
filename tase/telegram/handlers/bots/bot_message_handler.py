from typing import List

import pyrogram

from tase.my_logger import logger
from pyrogram import handlers
from pyrogram import filters

from tase.telegram.handlers import BaseHandler, HandlerMetadata


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
            message.reply_text(
                "An Error occurred while processing this audio download url"
            )

    def bot_message_handler(self, client: 'pyrogram.Client', message: 'pyrogram.types.Message'):
        logger.info(f"bot_message_handler: {message}")
