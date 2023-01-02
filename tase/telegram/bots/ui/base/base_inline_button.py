from __future__ import annotations

from typing import Optional, Dict, TYPE_CHECKING, List

import pyrogram
from pydantic import BaseModel, Field
from pyrogram.types import InlineKeyboardButton

from tase.common.utils import translate_text
from tase.db.arangodb import graph as graph_models
from tase.telegram.bots.ui.base.button_action_type import ButtonActionType
from tase.telegram.bots.ui.base.inline_button_type import InlineButtonType
from tase.telegram.update_handlers.base import BaseHandler
from tase.telegram.update_interfaces import (
    OnCallbackQuery,
    OnChosenInlineQuery,
    OnInlineQuery,
)

if TYPE_CHECKING:
    from tase.telegram.bots.inline import CustomInlineQueryResult
    from tase.telegram.bots.ui.base import InlineButtonData, InlineItemInfo, InlineItemType


class InlineButton(
    BaseModel,
    OnInlineQuery,
    OnChosenInlineQuery,
    OnCallbackQuery,
):
    __type__: InlineButtonType = Field(default=InlineButtonType.BASE)
    action: ButtonActionType = Field(default=ButtonActionType.CALLBACK)
    text: Optional[str]
    url: Optional[str]
    __switch_inline_query__: Optional[str] = Field(default=None)

    __valid_inline_items__: List[InlineItemType] = Field(default_factory=list)

    __registry__: Dict[int, InlineButton] = dict()
    __inline_registry__: Dict[str, InlineButton] = dict()

    @classmethod
    def __init_subclass__(cls) -> None:
        temp = cls()
        InlineButton.__registry__[temp.__type__.value] = temp

        if cls.switch_inline_query():
            InlineButton.__inline_registry__[temp.switch_inline_query()] = temp

    @classmethod
    def get_type_value(cls) -> int:
        return cls.__type__.value

    @classmethod
    def find_button_by_alias(cls, alias: str) -> Optional[InlineButton]:
        if not str:
            return None

        return cls.__inline_registry__.get(alias, None)

    @classmethod
    def find_button_by_type_value(
        cls,
        button_type_value: int,
    ) -> Optional[InlineButton]:
        """
        Find the InlineButton with the given `button_type_value`

        Parameters
        ----------
        button_type_value : int
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

        return cls.__registry__.get(button_type.value, None)

    def is_inline_other_chat(self) -> bool:
        return self.action == ButtonActionType.OTHER_CHAT_INLINE

    def is_inline(self) -> bool:
        return self.action == ButtonActionType.CURRENT_CHAT_INLINE

    def is_url(self) -> bool:
        return self.action == ButtonActionType.OPEN_URL

    def is_callback(self) -> bool:
        return self.action == ButtonActionType.CALLBACK

    @classmethod
    def switch_inline_query(cls) -> str:
        return cls.__switch_inline_query__

    @classmethod
    def get_keyboard(
        cls,
        *args,
        **kwargs,
    ) -> pyrogram.types.InlineKeyboardButton:
        raise NotImplementedError

    def __parse_keyboard_button__(
        self,
        *,
        lang_code: str = "en",
        callback_data=None,
        url: str = None,
        switch_inline_query_current_chat=None,
        switch_inline_query_other_chat=None,
    ) -> pyrogram.types.InlineKeyboardButton:
        return InlineKeyboardButton(
            text=self._get_text(lang_code),
            callback_data=callback_data,
            url=url,
            switch_inline_query_current_chat=switch_inline_query_current_chat,
            switch_inline_query=switch_inline_query_other_chat,
        )

    ############################################################
    def _get_translated_text(
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

    def _get_text(
        self,
        lang_code: str = "en",
    ) -> str:
        return self._get_translated_text(lang_code)

    ############################################################

    async def on_inline_query(
        self,
        handler: BaseHandler,
        result: CustomInlineQueryResult,
        from_user: graph_models.vertices.User,
        client: pyrogram.Client,
        telegram_inline_query: pyrogram.types.InlineQuery,
        query_date: int,
        inline_button_data: Optional[InlineButtonData] = None,
    ):
        raise NotImplementedError

    async def on_chosen_inline_query(
        self,
        handler: BaseHandler,
        client: pyrogram.Client,
        from_user: graph_models.vertices.User,
        telegram_chosen_inline_result: pyrogram.types.ChosenInlineResult,
        inline_button_data: InlineButtonData,
        inline_item_info: InlineItemInfo,
    ):
        raise NotImplementedError

    async def on_callback_query(
        self,
        handler: BaseHandler,
        from_user: graph_models.vertices.User,
        client: pyrogram.Client,
        telegram_callback_query: pyrogram.types.CallbackQuery,
        inline_button_data: InlineButtonData,
    ):
        raise NotImplementedError

    ######################################################################
    def is_inline_item_valid(self, inline_item_type: InlineItemType) -> bool:
        if not inline_item_type:
            return False

        return inline_item_type in self.__valid_inline_items__

    ######################################################################

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
