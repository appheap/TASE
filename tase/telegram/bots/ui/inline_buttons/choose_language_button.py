from typing import Optional, List

import pyrogram

from tase.common.utils import _trans
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.enums import ChatType
from tase.telegram.bots.ui.base import InlineButton, InlineButtonType, ButtonActionType, InlineButtonData
from tase.telegram.update_handlers.base import BaseHandler


class ChooseLanguageButtonData(InlineButtonData):
    __button_type__ = InlineButtonType.CHOOSE_LANGUAGE

    chat_type: ChatType
    chosen_language_code: str

    @classmethod
    def generate_data(
        cls,
        chat_type: ChatType,
        chosen_language_code: str,
    ) -> Optional[str]:
        return f"{cls.get_type_value()}|{chat_type.value}|{chosen_language_code}"

    @classmethod
    def __parse__(
        cls,
        data_split_lst: List[str],
    ) -> Optional[InlineButtonData]:
        if len(data_split_lst) != 3:
            return None

        return ChooseLanguageButtonData(
            chat_type=ChatType(int(data_split_lst[1])),
            chosen_language_code=data_split_lst[2],
        )


class ChooseLanguageInlineButton(InlineButton):
    __type__ = InlineButtonType.CHOOSE_LANGUAGE
    action = ButtonActionType.CALLBACK

    @classmethod
    def get_keyboard(
        cls,
        *,
        chat_type: ChatType,
        chosen_language_code: str,
        lang_code: Optional[str] = "en",
    ) -> pyrogram.types.InlineKeyboardButton:
        return cls.get_button(cls.__type__).__parse_keyboard_button__(
            callback_data=ChooseLanguageButtonData.generate_data(chat_type, chosen_language_code),
            lang_code=lang_code,
        )

    async def on_callback_query(
        self,
        handler: BaseHandler,
        from_user: graph_models.vertices.User,
        client: pyrogram.Client,
        telegram_callback_query: pyrogram.types.CallbackQuery,
        inline_button_data: ChooseLanguageButtonData,
    ):
        await from_user.update_chosen_language(inline_button_data.chosen_language_code)
        text = _trans(
            "Language change has been saved",
            lang_code=inline_button_data.chosen_language_code,
        )
        await telegram_callback_query.answer(
            text,
            show_alert=False,
        )
        await telegram_callback_query.message.delete()
