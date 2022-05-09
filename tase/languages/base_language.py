from pydantic import BaseModel


class Language(BaseModel):
    code: str
    flag: str
    name: str

    def choose_language_text(self) -> str:
        return f" {self.flag} {self.name}"

    def get_choose_language_callback_data(self) -> str:
        return f"choose_language->{self.code}"
