from typing import Dict

from .base_language import Language
from .languages import Languages
from ..static import Emoji

emoji: Emoji = Emoji()

english = Language(
    code='en',
    flag=emoji._usa_flag,
    name='English'
)
persian = Language(
    code='fa',
    flag=emoji._iran_flag,
    name='فارسی (Persian)'
)
arabic = Language(
    code='ar',
    flag=emoji._saudi_arabia_flag,
    name='العربية (Arabic)'
)

language_mapping: Dict[str, Language] = {
    'en': english,
    'fa': persian,
    'ar': arabic,
}
languages_object = Languages(
    mappings=language_mapping,
)

__all__ = [
    'Language',
    'languages_object'
]
