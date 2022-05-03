import unicodedata

from jinja2 import Template
from pydantic import BaseModel

from static.emoji import Emoji
from tase.utils import translate_text


class BaseTemplateData(BaseModel):
    emoji: Emoji = Emoji()

    c_new_line: str = "\n"
    c_dir: str = "&lrm;"
    c_query: str

    lang_code: str = 'en'

    def update_translations(self) -> 'BaseTemplateData':
        temp_dict = self.dict()
        if self.lang_code != 'en':
            for attr_name, attr_value in temp_dict.items():
                if attr_name.startswith('s_'):
                    setattr(self, attr_name, translate_text(attr_value, self.lang_code))

        x = len(
            [None for ch in self.c_query if unicodedata.bidirectional(ch) in ('R', 'AL')]
        ) / float(len(self.c_query))
        self.c_dir = "&rlm;" if x > 0.5 else '&lrm;'

        return self


class BaseTemplate:
    template: Template

    def render(self, data) -> str:
        return self.template.render(data.update_translations())
