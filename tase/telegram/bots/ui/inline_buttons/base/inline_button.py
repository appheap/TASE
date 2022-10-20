from __future__ import annotations

from typing import Match, Optional

import pyrogram
from pydantic import BaseModel, Field
from pyrogram.types import InlineKeyboardButton

from tase.common.utils import translate_text
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.enums import ChatType
from tase.telegram.bots.inline import CustomInlineQueryResult
from tase.telegram.bots.ui.inline_buttons.base.inline_button_type import (
    InlineButtonType,
)
from tase.telegram.update_handlers.base import BaseHandler
from tase.telegram.update_interfaces import (
    OnCallbackQuery,
    OnChosenInlineQuery,
    OnInlineQuery,
)


class InlineButton(
    BaseModel,
    OnInlineQuery,
    OnChosenInlineQuery,
    OnCallbackQuery,
):
    _registry = dict()
    name: str
    type: InlineButtonType = Field(default=InlineButtonType.BASE)

    text: Optional[str]
    is_inline: bool = Field(default=False)
    is_url: bool = Field(default=False)
    url: Optional[str]

    @classmethod
    def __init_subclass__(cls) -> None:
        temp = cls()
        InlineButton._registry[temp.type.value] = temp

    @classmethod
    def find_button_by_type_value(
        cls,
        button_type_value: str,
    ) -> Optional[InlineButton]:
        """
        Find the InlineButton with the given `button_type_value`

        Parameters
        ----------
        button_type_value : str
            Value of `InlineButtonType` to find the inline button by

        Returns
        -------
        InlineButton, optional
            InlineButton with the `button_type_value` if exists, otherwise, return None

        """
        button_type = InlineButtonType.UNKNOWN
        for e in list(InlineButtonType):
            if e.value == button_type_value:
                button_type = e
                break

        return cls.get_button(button_type)

    @classmethod
    def get_button(
        cls,
        button_type: InlineButtonType,
    ) -> Optional[InlineButton]:
        if button_type is None and button_type not in (
            InlineButtonType.BASE,
            InlineButtonType.UNKNOWN,
            InlineButtonType.INVALID,
        ):
            return None

        return cls._registry.get(button_type.value, None)

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

    def new_text(
        self,
        *args,
        **kwargs,
    ) -> str:
        raise NotImplementedError

    def change_text(
        self,
        *args,
        **kwargs,
    ) -> InlineButton:
        raise NotImplementedError

    def get_url(
        self,
        url: str,
    ) -> str:
        if url is None:
            return self.url
        return url

    def get_callback_data(
        self,
        chat_type: ChatType,
        callback_arg=None,
    ) -> Optional[str]:
        if self.is_inline or self.is_url:
            return None
        return f"{self.type.value}->{callback_arg}->{chat_type.value}"

    def get_switch_inline_query_current_chat(
        self,
        arg=None,
    ) -> Optional[str]:
        return f"#{self.type.value} {arg}" if arg is not None else f"#{self.type.value}"

    def get_inline_keyboard_button(
        self,
        lang_code: str = "en",
        switch_inline_arg=None,
        callback_arg=None,
        url: str = None,
        chat_type: ChatType = ChatType.BOT,
    ):
        return InlineKeyboardButton(
            text=self.get_text(lang_code),
            callback_data=self.get_callback_data(chat_type, callback_arg),
            url=self.get_url(url),
            switch_inline_query_current_chat=self.get_switch_inline_query_current_chat(
                switch_inline_arg,
            ),
        )

    ############################################################

    def on_inline_query(
        self,
        handler: BaseHandler,
        result: CustomInlineQueryResult,
        from_user: graph_models.vertices.User,
        client: pyrogram.Client,
        telegram_inline_query: pyrogram.types.InlineQuery,
        query_date: int,
        reg: Optional[Match] = None,
    ):
        raise NotImplementedError

    def on_chosen_inline_query(
        self,
        handler: BaseHandler,
        client: pyrogram.Client,
        from_user: graph_models.vertices.User,
        telegram_chosen_inline_result: pyrogram.types.ChosenInlineResult,
        reg: Match,
    ):
        raise NotImplementedError

    def on_callback_query(
        self,
        handler: BaseHandler,
        from_user: graph_models.vertices.User,
        client: pyrogram.Client,
        telegram_callback_query: pyrogram.types.CallbackQuery,
    ):
        raise NotImplementedError
