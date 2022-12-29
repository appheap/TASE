from pydantic import BaseModel

from tase.db.arangodb.enums import ChatType


class Language(BaseModel):
    code: str
    flag: str
    name: str

    def choose_language_text(self) -> str:
        return f" {self.flag} {self.name}"

    def get_choose_language_callback_data(self) -> str:
        from tase.telegram.bots.ui.base import InlineButtonType

        return f"{InlineButtonType.CHOOSE_LANGUAGE.value}|{ChatType.BOT.value}|{self.code}"
