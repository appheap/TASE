from typing import Optional, Match

import pyrogram
from pydantic import BaseModel
from pyrogram.types import InlineKeyboardButton

from tase.db import DatabaseClient, graph_models
# from ..telegram_client import TelegramClient
# from tase.telegram.handlers import BaseHandler
from tase.utils import translate_text


class InlineButton(BaseModel):
    _registry = dict()
    name: str

    text: Optional[str]
    callback_data: Optional[str]
    switch_inline_query_current_chat: Optional[str]
    url: Optional[str]

    @classmethod
    def __init_subclass__(cls) -> None:
        temp = cls()
        InlineButton._registry[temp.name] = temp

    @classmethod
    def get_button(cls, name: str) -> Optional['InlineButton']:
        if name is None:
            return None
        return cls._registry.get(name, None)

    def get_translated_text(self, lang_code: str = 'en') -> str:
        temp_dict = self.dict()

        temp = ""

        if not lang_code or lang_code != 'en':
            for attr_name, attr_value in temp_dict.items():
                if attr_name.startswith('s_'):
                    if not len(temp):
                        temp = self.text.replace(attr_value, translate_text(attr_value, lang_code))
                    else:
                        temp = temp.replace(attr_value, translate_text(attr_value, lang_code))

        return temp if len(temp) else self.text

    def get_text(self, lang_code: str = 'en') -> str:
        return self.get_translated_text(lang_code)

    def get_url(self) -> str:
        return self.url

    def get_callback_data(self) -> Optional[str]:
        return self.callback_data

    def get_switch_inline_query_current_chat(self, arg=None) -> Optional[str]:
        return f"{self.switch_inline_query_current_chat} {arg}" if arg else self.switch_inline_query_current_chat

    def get_inline_keyboard_button(self, lang_code: str = 'en', arg=None):
        return InlineKeyboardButton(
            text=self.get_text(lang_code),
            callback_data=self.get_callback_data(),
            url=self.get_url(),
            switch_inline_query_current_chat=self.get_switch_inline_query_current_chat(arg)
        )

    ############################################################

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
        raise NotImplementedError

    def on_chosen_inline_query(
            self,
            client: 'pyrogram.Client',
            chosen_inline_result: 'pyrogram.types.ChosenInlineResult',
            handler: 'BaseHandler',
            db: 'DatabaseClient',
            telegram_client: 'TelegramClient',
            db_from_user: graph_models.vertices.User,
            reg: Match,
    ):
        raise NotImplementedError

    def on_callback_query(
            self,
            client: 'pyrogram.Client',
            callback_query: 'pyrogram.types.CallbackQuery',
            handler: 'BaseHandler',
            db: 'DatabaseClient',
            telegram_client: 'TelegramClient',
            db_from_user: graph_models.vertices.User,
    ):
        raise NotImplementedError
