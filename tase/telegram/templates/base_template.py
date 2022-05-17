import unicodedata
from typing import Optional

from jinja2 import Template
from pydantic import BaseModel

from tase.static import Emoji
from tase.utils import translate_text


class BaseTemplateData(BaseModel):
    emoji: Emoji = Emoji()

    c_new_line: str = "\n"
    c_dir: str = "&lrm;"
    c_sep: str = "-" * 34
    c_hidden_char: str = "‏‏‎ ‎"

    lang_code: Optional[str] = 'en'

    def update_translations(self) -> 'BaseTemplateData':
        temp_dict = self.dict()

        c_dir_done = False

        query = temp_dict.get('query', None)
        if query:
            self.set_direction_from(query)
            c_dir_done = True

        if not self.lang_code or self.lang_code != 'en':
            for attr_name, attr_value in temp_dict.items():
                if attr_name.startswith('s_'):
                    setattr(self, attr_name, translate_text(attr_value, self.lang_code))
                    if not c_dir_done:
                        value = getattr(self, attr_name)
                        self.set_direction_from(value)
                        c_dir_done = True

        return self

    def set_direction_from(self, value: str):
        if value is None:
            raise Exception('value cannot be None')
        x = len(
            [None for ch in value if unicodedata.bidirectional(ch) in ('R', 'AL')]
        ) / float(len(value))
        self.c_dir = "&rlm;" if x > 0.5 else '&lrm;'


class TemplateRegistry:
    pass


class BaseTemplate:
    template: Template

    name: str = ""
    registry = TemplateRegistry()

    def render(self, data) -> str:
        return self.template.render(data.update_translations())

    @classmethod
    def __init_subclass__(cls, **kwargs):
        temp = cls()
        setattr(BaseTemplate.registry, cls.name, temp)
