from typing import Dict, Optional

from pydantic import BaseModel
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from .base_language import Language


class Languages(BaseModel):
    mappings: Dict[str, Language]

    def get_choose_language_markup(self) -> InlineKeyboardMarkup:
        markup_list = []
        for language in self.mappings.values():
            markup_list.append(
                [
                    InlineKeyboardButton(
                        text=language.choose_language_text(),
                        callback_data=language.get_choose_language_callback_data()
                    )
                ]
            )

        return InlineKeyboardMarkup(markup_list)

    def get_language_by_code(self, lang_code: str) -> Optional[Language]:
        if lang_code is None:
            return None
        return self.mappings.get(lang_code, None)
