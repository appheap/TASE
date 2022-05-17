from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Callable, Union

import kombu
import pyrogram
from pydantic import BaseModel
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardMarkup

from tase.db import graph_models, elasticsearch_models
from tase.db.database_client import DatabaseClient
from tase.my_logger import logger
from tase.utils import languages_object
from .handler_metadata import HandlerMetadata
from ... import template_globals
from ...inline_buttons import InlineButton
from ...telegram_client import TelegramClient
from ...templates import HomeData, ChooseLanguageData, WelcomeData, HelpData


def exception_handler(func: 'Callable'):
    def wrap(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            logger.exception(e)

    return wrap


class BaseHandler(BaseModel):
    db: 'DatabaseClient'
    task_queues: Dict['str', 'kombu.Queue']
    telegram_client: 'TelegramClient'

    class Config:
        arbitrary_types_allowed = True

    def init_handlers(self) -> List['HandlerMetadata']:
        raise NotImplementedError

    def update_audio_cache(
            self,
            db_audios: Union[List[graph_models.vertices.Audio], List[elasticsearch_models.Audio]]
    ) -> Dict[int, graph_models.vertices.Chat]:
        """
        Update Audio file caches that are not been cached by this telegram client

        :param db_audios: List of audios to be checked
        :return: A dictionary mapping from `chat_id` to a Chat object
        """
        chat_msg = defaultdict(list)
        chats_dict = {}
        for db_audio in db_audios:
            if not self.db.get_audio_file_from_cache(db_audio, self.telegram_client.telegram_id):
                chat_msg[db_audio.chat_id].append(db_audio.message_id)

            if not chats_dict.get(db_audio.chat_id, None):
                db_chat = self.db.get_chat_by_chat_id(db_audio.chat_id)

                chats_dict[db_chat.chat_id] = db_chat

        for chat_id, message_ids in chat_msg.items():
            db_chat = chats_dict[chat_id]

            # todo: this approach is only for public channels, what about private channels?
            messages = self.telegram_client.get_messages(chat_id=db_chat.username, message_ids=message_ids)

            for message in messages:
                self.db.update_or_create_audio(
                    message,
                    self.telegram_client.telegram_id,
                )
        return chats_dict

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
            url1='https://github.com/appheap/TASE',
            url2='https://github.com/appheap/TASE',
            lang_code=db_from_user.chosen_language_code,
        )

        markup = [
            [
                InlineButton.get_button('download_history').get_inline_keyboard_button(
                    db_from_user.chosen_language_code),
                InlineButton.get_button('my_playlists').get_inline_keyboard_button(db_from_user.chosen_language_code),
            ],
            [
                InlineButton.get_button('back').get_inline_keyboard_button(db_from_user.chosen_language_code),
            ],
            [
                InlineButton.get_button('advertisement').get_inline_keyboard_button(db_from_user.chosen_language_code),
                InlineButton.get_button('help_catalog').get_inline_keyboard_button(db_from_user.chosen_language_code),
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
    ) -> None:
        """
        Ask users to choose a language among a menu shows a list of available languages.

        :param client: Telegram client
        :param db_from_user: User Object from the graph database
        :return:
        """
        data = ChooseLanguageData(
            name=db_from_user.first_name or db_from_user.last_name,
            lang_code=db_from_user.chosen_language_code,
        )

        client.send_message(
            chat_id=db_from_user.user_id,
            text=template_globals.choose_language_template.render(data),
            reply_markup=languages_object.get_choose_language_markup(),
            parse_mode=ParseMode.HTML
        )

    def show_home(
            self,
            client: 'pyrogram.Client',
            db_from_user: graph_models.vertices.User,
            message: 'pyrogram.types.Message'
    ) -> None:
        """
        Shows the Home menu

        :param client: Telegram client
        :param db_from_user: User Object from the graph database
        :param message: Telegram message object
        :return:
        """
        data = HomeData(
            support_channel_username='support_channel_username',
            url1='https://github.com/appheap/TASE',
            url2='https://github.com/appheap/TASE',
            lang_code=db_from_user.chosen_language_code,
        )

        markup = [
            [
                InlineButton.get_button('download_history').get_inline_keyboard_button(
                    db_from_user.chosen_language_code),
                InlineButton.get_button('my_playlists').get_inline_keyboard_button(db_from_user.chosen_language_code),
            ],
            [
                InlineButton.get_button('show_language_menu').get_inline_keyboard_button(
                    db_from_user.chosen_language_code),
            ],
            [
                InlineButton.get_button('advertisement').get_inline_keyboard_button(db_from_user.chosen_language_code),
                InlineButton.get_button('help_catalog').get_inline_keyboard_button(db_from_user.chosen_language_code),
            ]
        ]
        markup = InlineKeyboardMarkup(markup)

        chat_id = None
        if message:
            if message.chat:
                chat_id = message.chat.id
            elif message.from_user:
                chat_id = message.from_user.id
        else:
            chat_id = db_from_user.user_id

        client.send_message(
            chat_id=chat_id,
            text=template_globals.home_template.render(data),
            parse_mode=ParseMode.HTML,
            reply_markup=markup,
        )
