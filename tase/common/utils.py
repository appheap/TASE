import collections
import gettext
import json
import os
import re
import secrets
import time
from collections import OrderedDict
from datetime import datetime
from functools import wraps
from typing import Optional, List, Tuple, Dict, Match, Union, Callable, Any

import arrow
import psutil
import tomli
from pydantic import BaseModel

from tase.common.preprocessing import clean_hashtag, hashtags_regex, is_non_digit
from tase.db.arangodb.enums import MentionSource
from tase.errors import NotEnoughRamError
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

language_mapping: Dict[str, Language] = {
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
    POSTFIX = "../locales"

    cwd = os.getcwd()
    cwd = cwd[cwd.find("TASE/") :]

    if cwd.endswith("tase"):
        localedir = POSTFIX
    else:
        if "tase" in cwd:
            localedir = "../" * (cwd.count("/") - 1) + POSTFIX
        else:
            localedir = "../" * (cwd.count("/")) + "tase/" + POSTFIX

    for lang_code in language_mapping.keys():
        logger.debug(f"lang_code: {lang_code}")
        lang = gettext.translation("tase", localedir=localedir, languages=[lang_code])
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
) -> Optional[Dict]:
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
    if isinstance(obj, Match):
        return repr(obj)
    return (
        OrderedDict(
            {
                "_": obj.__class__.__name__,
                **{attr: getattr(obj, attr) for attr in filter(lambda x: not x.startswith("_"), obj.__dict__) if getattr(obj, attr) is not None},
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
    if isinstance(obj, Match):
        return repr(obj)
    return (
        OrderedDict({**{attr: getattr(obj, attr) for attr in filter(lambda x: not x.startswith("_"), obj.__dict__) if getattr(obj, attr) is not None}})
        if hasattr(obj, "__dict__")
        else None
    )


def prettify(
    obj: object,
    sort_keys=False,
    include_class_name=True,
) -> str:
    return json.dumps(
        obj,
        indent=4,
        default=default if include_class_name else default_no_class_name,
        sort_keys=sort_keys,
        ensure_ascii=False,
    )


def datetime_to_timestamp(date: datetime) -> Optional[int]:
    """
    Convert a `datetime` object into UTC timestamp in milliseconds.

    Parameters
    ----------
    date : datetime
        Datetime object to be converted

    Returns
    -------
    int, optional
        UTC timestamp in milliseconds


    """
    if date is not None:
        # fixme: make sure this returns utc timestamp
        return int(date.timestamp() * 1000)
    return None


def get_now_timestamp() -> int:
    """
    Get UTC timestamp in milliseconds

    Returns
    -------
    int
        UTC Timestamp in milliseconds

    """
    return int(arrow.utcnow().timestamp() * 1000)


def check_ram_usage(threshold: int = 90) -> None:
    """
    Check if the RAM usage is below the given threshold

    Parameters
    ----------
    threshold : int
        RAM usage threshold

    Raises
    ------
    NotEnoughRamError
        In case the RAM usage is greater than given threshold
    """
    if psutil.virtual_memory().percent > threshold:
        raise NotEnoughRamError(threshold)


def sync_timed(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()

        logger.debug(f"sync func:{f.__name__}  took: {round((te - ts) * 1000):} ms")
        return result

    return wrap


def async_timed():
    def wrapper(func: Callable) -> Callable:
        @wraps(func)
        async def wrapped(*args, **kwargs) -> Any:
            start = time.time()
            try:
                return await func(*args, **kwargs)
            finally:
                end = time.time()
                logger.debug(f"async func:{func.__name__}  took: {round((end - start) * 1000):} ms")

        return wrapped

    return wrapper


def async_exception_handler():
    def wrapper(func: Callable) -> Callable:
        @wraps(func)
        async def wrapped(*args, **kwargs) -> Any:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.exception(e)

        return wrapped

    return wrapper


def sync_exception_handler(func: Callable):
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
                    setattr(
                        old_doc,
                        attr_name,
                        copy_attrs_from_new_document(old_value, new_value),
                    )
            else:
                setattr(old_doc, attr_name, new_value)

    return old_doc


def generate_token_urlsafe(
    nbytes: int = 6,
):
    while True:
        # todo: make sure the generated token is unique
        download_url = secrets.token_urlsafe(nbytes)
        if download_url.find("-") == -1:
            break
    return download_url


def find_hashtags(
    text: str,
    mention_source: MentionSource = None,
) -> List[Tuple[str, int, MentionSource]]:
    if text is None:
        return []

    text = clean_hashtag(text)

    hashtags = collections.deque()
    for match in re.finditer(hashtags_regex, text):
        h = match.group("hashtag")
        if is_non_digit(h[1:]):
            hashtags.append((h, match.start(), mention_source))

    return list(hashtags)


def find_unique_hashtag_strings(
    text_: str,
    remove_hashtag_sign: Optional[bool] = True,
) -> List[str]:
    if not text_:
        return []

    text_ = clean_hashtag(text_)
    if not text_:
        return []

    hashtags = set()
    for match in re.finditer(hashtags_regex, text_):
        h = str(match.group("hashtag"))
        if is_non_digit(h[1:]):
            hashtags.add(h[1:] if remove_hashtag_sign else h)

    return list(hashtags)


def find_hashtags_in_text(
    text: Union[str, List[Union[str, None]]],
    mention_source: Union[MentionSource, List[MentionSource]],
) -> List[Tuple[str, int, MentionSource]]:
    """
    Find hashtags in the given text.

    Parameters
    ----------
    text : str | list of str
        A string or an array of strings to check.
    mention_source : MentionSource | list of MentionSource
        A `MentionSource` object or a list of `MentionSource` objects.

    Returns
    -------
    list
        A list containing a tuple of the `hashtag` string, its starting index, and its mention source.

    Raises
    ------
    ValueError
        If input data is invalid.

    """
    if text is None or not len(text) or mention_source is None:
        return []

    hashtags = collections.deque()

    if not isinstance(text, str) and isinstance(text, List):
        if isinstance(mention_source, List):
            if len(mention_source) != len(text):
                raise ValueError(f"mention_source and text must of the the same size: {len(mention_source)} != " f"{len(text)}")

            for text__, mention_source_ in zip(text, mention_source):
                if text__ is not None and mention_source_ is not None:
                    hashtags.extend(find_hashtags(text__, mention_source_))
        else:
            for text__ in text:
                if text__ is not None:
                    hashtags.extend(find_hashtags(text__, mention_source))

    else:
        if text is not None:
            hashtags.extend(find_hashtags(text, mention_source))

    return list(hashtags)


def group_list_by_step(
    l: List[Any],
    step: int = 100,
) -> List[List[Any]]:
    return [l[i : i + step] for i in range(0, len(l), step)]
