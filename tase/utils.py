import gettext
import json
import typing
from collections import OrderedDict
from functools import wraps
from time import time
from typing import Optional

import arrow
import tomli
from pydantic import BaseModel

from tase.languages import Language, Languages
from tase.my_logger import logger
from tase.static import Emoji

# todo: it's not a good practice to hardcode like this, fix it
languages = dict()

emoji: Emoji = Emoji()

english = Language(code="en", flag=emoji._usa_flag, name="English")

russian = Language(code="ru", flag=emoji._russia_flag, name="русский (Russian)")

indian = Language(code="hi", flag=emoji._india_flag, name="िन्दी (Hindi)")

german = Language(code="de", flag=emoji._germany_flag, name="Deutsch (German)")

dutch = Language(code="nl", flag=emoji._netherlands_flag, name="Dutch (Nederlands)")

portugues = Language(code="pt_BR", flag=emoji._portugal_flag, name="Português (Portuguese)")

persian = Language(code="fa", flag=emoji._iran_flag, name="فارسی (Persian)")
arabic = Language(code="ar", flag=emoji._saudi_arabia_flag, name="العربية (Arabic)")

kurdish_sorani = Language(code="ku", flag=emoji._tajikistan_flag, name="کوردی سۆرانی (Sorani Kurdish)")

kurdish_kurmanji = Language(code="ku_TR", flag=emoji._lithuania_flag, name="(Kurmanji Kurdish) Kurdî Kurmancî")

italian = Language(code="it", flag=emoji._italy_flag, name="Italiana (Italian)")

spanish = Language(code="es", flag=emoji._spain_flag, name="Español (Spanish)")

language_mapping: typing.Dict[str, Language] = {
    "en": english,
    "ru": russian,
    "hi": indian,
    "de": german,
    "nl": dutch,
    "pt_BR": portugues,
    "it": italian,
    "es": spanish,
    "fa": persian,
    "ar": arabic,
    "ku": kurdish_sorani,
    "ku_TR": kurdish_kurmanji,
}

if not len(languages):
    for lang_code in language_mapping.keys():
        logger.debug(f"lang_code: {lang_code}")
        lang = gettext.translation("tase", localedir="../locales", languages=[lang_code])
        lang.install()
        languages[lang_code] = lang.gettext


def _trans(
    text: str,
    lang_code: str = "en",
) -> str:
    """
    Translates the given text to another language given by the `lang_code` parameter

    :param text: The text to be translated
    :param lang_code: Code of the language to be translated to. Default is `en` for English
    :return: The translated text
    """
    return translate_text(text, lang_code)


def translate_text(
    text: str,
    lang_code: str = "en",
) -> str:
    """
    Translates the given text to another language given by the `lang_code` parameter

    :param text: The text to be translated
    :param lang_code: Code of the language to be translated to. Default is `en` for English
    :return: The translated text
    """
    return languages.get(lang_code, languages["en"])(text)


languages_object = Languages(
    mappings=language_mapping,
)


def _get_config_from_file(
    file_path: str,
) -> Optional["dict"]:
    try:
        with open(file_path, "rb") as f:
            return tomli.load(f)
    except tomli.TOMLDecodeError as e:
        logger.exception(e)
    except Exception as e:
        logger.exception(e)

    return None


def default(obj: object):
    if obj is None:
        return None
    if isinstance(obj, bytes):
        return repr(obj)

    # https://t.me/pyrogramchat/167281
    # Instead of re.Match, which breaks for python <=3.6
    if isinstance(obj, typing.Match):
        return repr(obj)
    return (
        OrderedDict(
            {
                "_": obj.__class__.__name__,
                **{
                    attr: getattr(obj, attr)
                    for attr in filter(lambda x: not x.startswith("_"), obj.__dict__)
                    if getattr(obj, attr) is not None
                },
            }
        )
        if hasattr(obj, "__dict__")
        else None
    )


def default_no_class_name(obj: object):
    if obj is None:
        return None
    if isinstance(obj, bytes):
        return repr(obj)

    # https://t.me/pyrogramchat/167281
    # Instead of re.Match, which breaks for python <=3.6
    if isinstance(obj, typing.Match):
        return repr(obj)
    return (
        OrderedDict(
            {
                **{
                    attr: getattr(obj, attr)
                    for attr in filter(lambda x: not x.startswith("_"), obj.__dict__)
                    if getattr(obj, attr) is not None
                }
            }
        )
        if hasattr(obj, "__dict__")
        else None
    )


def prettify(
    obj: object,
    sort_keys=False,
    include_class_name=True,
) -> "str":
    return json.dumps(
        obj,
        indent=4,
        default=default if include_class_name else default_no_class_name,
        sort_keys=sort_keys,
        ensure_ascii=False,
    )


def get_timestamp(
    date=None,
) -> int:
    if date is not None:
        # fixme: make sure this returns utc timestamp
        return int(arrow.get(date).timestamp())
    return int(arrow.utcnow().timestamp())


def timing(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()

        # fixme
        # logger.info("func:%r args:[%r, %r] took: %2.4f sec" % (f.__name__, args, kw, te - ts))
        logger.error("func:%r  took: %2.4f sec" % (f.__name__, te - ts))
        return result

    return wrap


def exception_handler(func: "typing.Callable"):
    def wrap(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            logger.exception(e)

    return wrap


def copy_attrs_from_new_document(
    old_doc: BaseModel,
    new_doc: BaseModel,
) -> Optional[BaseModel]:
    """
    Copy an object attributes recursively from another object.

    Parameters
    ----------
    old_doc : BaseModel
        Object to update its attributes

    new_doc : BaseModel
        Object to get the new attributes from

    Returns
    -------
    Optional[BaseModel]
        Updated object if successful, otherwise return `None`
    """
    if old_doc is None or new_doc is None:
        return None
    for attr_name in old_doc.__dict__:
        old_value = getattr(old_doc, attr_name, None)
        new_value = getattr(new_doc, attr_name, None)

        # logger.info(f"{attr_name} : {old_value} : {new_value}")
        if new_value is None:
            setattr(old_doc, attr_name, None)
        else:
            if isinstance(new_value, BaseModel):
                if old_value is None:
                    setattr(old_doc, attr_name, new_value)
                else:
                    setattr(old_doc, attr_name, copy_attrs_from_new_document(old_value, new_value))
            else:
                setattr(old_doc, attr_name, new_value)

    return old_doc
