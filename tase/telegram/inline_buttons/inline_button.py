from typing import Match, Optional

import pyrogram
from pydantic import BaseModel
from pyrogram.types import InlineKeyboardButton

from tase.db import graph_models
from tase.utils import translate_text
from ..inline import CustomInlineQueryResult
from ..interfaces import OnCallbackQuery, OnChosenInlineQuery, OnInlineQuery


class InlineButton(
    BaseModel,
    OnInlineQuery,
    OnChosenInlineQuery,
    OnCallbackQuery,
):
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
    def get_button(
        cls,
        name: str,
    ) -> Optional["InlineButton"]:
        if name is None:
            return None
        return cls._registry.get(name, None)

    def get_translated_text(
        self,
        lang_code: str = "en",
    ) -> str:
        temp_dict = self.dict()

        temp = ""

        if not lang_code or lang_code != "en":
            for attr_name, attr_value in temp_dict.items():
                if attr_name.startswith("s_"):
                    if not len(temp):
                        temp = self.text.replace(attr_value, translate_text(attr_value, lang_code))
                    else:
                        temp = temp.replace(attr_value, translate_text(attr_value, lang_code))

        return temp if len(temp) else self.text

    def get_text(
        self,
        lang_code: str = "en",
    ) -> str:
        return self.get_translated_text(lang_code)

    def get_url(self) -> str:
        return self.url

    def get_callback_data(self, callback_arg=None) -> Optional[str]:
        if callback_arg is None:
            return self.callback_data
        else:
            data, arg = self.callback_data.split("->")
            return f"{data}->{callback_arg}"

    def get_switch_inline_query_current_chat(
        self,
        arg=None,
    ) -> Optional[str]:
        return f"{self.switch_inline_query_current_chat} {arg}" if arg else self.switch_inline_query_current_chat

    def get_inline_keyboard_button(
        self,
        lang_code: str = "en",
        switch_inline_query_current_chat=None,
        callback_arg=None,
    ):
        return InlineKeyboardButton(
            text=self.get_text(lang_code),
            callback_data=self.get_callback_data(callback_arg),
            url=self.get_url(),
            switch_inline_query_current_chat=self.get_switch_inline_query_current_chat(
                switch_inline_query_current_chat,
            ),
        )

    ############################################################

    def on_inline_query(
        self,
        handler: "BaseHandler",
        result: CustomInlineQueryResult,
        db_from_user: "graph_models.vertices.User",
        client: "pyrogram.Client",
        inline_query: "pyrogram.types.InlineQuery",
        query_date: int,
        reg: Optional[Match] = None,
    ):
        raise NotImplementedError

    def on_chosen_inline_query(
        self,
        handler: "BaseHandler",
        client: "pyrogram.Client",
        db_from_user: graph_models.vertices.User,
        chosen_inline_result: "pyrogram.types.ChosenInlineResult",
        reg: Match,
    ):
        raise NotImplementedError

    def on_callback_query(
        self,
        handler: "BaseHandler",
        db_from_user: "graph_models.vertices.User",
        client: "pyrogram.Client",
        callback_query: "pyrogram.types.CallbackQuery",
    ):
        raise NotImplementedError
