import collections
import gettext
import json
import re
import secrets
from collections import OrderedDict
from datetime import datetime
from functools import wraps
from time import time
from typing import Optional, List, Tuple, Dict, Match, Union, Any

import arrow
import tomli
from pydantic import BaseModel
from pyrogram.types import BotCommand, BotCommandScopeChat, BotCommandScopeDefault

from tase.db.arangodb import graph as graph_models
from tase.languages import Language, Languages
from tase.my_logger import logger
from tase.static import Emoji
from .preprocessing import telegram_url_regex, hashtags_regex, clean_hashtag
from ..db.arangodb.enums import MentionSource
from ..db.arangodb.graph.vertices.user import UserRole
from ..telegram.bots.bot_commands import BaseCommand, BotCommandType

# todo: it's not a good practice to hardcode like this, fix it
languages = dict()

emoji: Emoji = Emoji()

english = Language(code="en", flag=emoji._usa_flag, name="English")

russian = Language(code="ru", flag=emoji._russia_flag, name="русский (Russian)")

indian = Language(code="hi", flag=emoji._india_flag, name="िन्दी (Hindi)")

german = Language(code="de", flag=emoji._germany_flag, name="Deutsch (German)")

dutch = Language(code="nl", flag=emoji._netherlands_flag, name="Dutch (Nederlands)")

portugues = Language(
    code="pt_BR", flag=emoji._portugal_flag, name="Português (Portuguese)"
)

persian = Language(code="fa", flag=emoji._iran_flag, name="فارسی (Persian)")
arabic = Language(code="ar", flag=emoji._saudi_arabia_flag, name="العربية (Arabic)")

kurdish_sorani = Language(
    code="ku", flag=emoji._tajikistan_flag, name="کوردی سۆرانی (Sorani Kurdish)"
)

kurdish_kurmanji = Language(
    code="ku_TR", flag=emoji._lithuania_flag, name="(Kurmanji Kurdish) Kurdî Kurmancî"
)

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
    for lang_code in language_mapping.keys():
        logger.debug(f"lang_code: {lang_code}")
        lang = gettext.translation(
            "tase", localedir="../locales", languages=[lang_code]
        )
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
    if isinstance(obj, Match):
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
    if isinstance(obj, Match):
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


def datetime_to_timestamp(date: Optional[datetime]) -> Optional[int]:
    if date is not None:
        # fixme: make sure this returns utc timestamp
        return int(date.timestamp())
    return None


def get_now_timestamp() -> int:
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


def find_telegram_usernames(text: str) -> Optional[List[Tuple[str, int]]]:
    """
    Find telegram usernames in the given text

    Parameters
    ----------
    text : str
        Text to extract the usernames from

    Returns
    -------
    list of tuple of str and int, optional
        List of tuple of username and starting index of the regex match if successful, otherwise, return an empty list

    """
    if text is None:
        return []

    usernames = collections.deque()
    for match in re.finditer(telegram_url_regex, text):
        username0 = match.group("username0")
        username1 = match.group("username1")

        if username0 is not None:
            username = username0
        elif username1 is not None:
            username = username1
        else:
            continue
        usernames.append((username, match.start()))

    return list(usernames)


def find_hashtags(
    text: str,
    mention_source: MentionSource = None,
) -> List[Tuple[str, int, MentionSource]]:
    if text is None:
        return []

    text = clean_hashtag(text)

    hashtags = collections.deque()
    for match in re.finditer(hashtags_regex, text):
        hashtags.append((match.group(), match.start(), mention_source))

    return list(hashtags)


def find_hashtags_in_text(
    text: Union[str, List[Union[str, None]]],
    mention_source: Union[MentionSource, List[MentionSource]],
) -> List[Tuple[str, int, MentionSource]]:
    if text is None or not len(text) or mention_source is None:
        return []

    hashtags = collections.deque()
    if not isinstance(text, str) and isinstance(text, List):
        if isinstance(mention_source, List):
            if len(mention_source) != len(text):
                raise Exception(
                    f"mention_source and text must of the the same size: {len(mention_source)} != "
                    f"{len(text)}"
                )
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


def get_bot_commands_list_for_telegram(
    admins_and_owners: List[graph_models.vertices.User],
) -> List[Dict[str, Any]]:
    """
    Get list of bot commands along with scope of the commands used in Telegram

    Parameters
    ----------
    admins_and_owners : list of graph_models.vertices.User
        List of `User` vertices that are their role is either `admin` or `owner`

    Returns
    -------
    list[dict[str, any]]
        List of dictionary containing the scope of a bot command and list of bot commands

    """

    def populate_commands(role: UserRole) -> List[BaseCommand]:
        commands = collections.deque()
        for command in sorted(
            filter(
                lambda c: c is not None,
                map(
                    BaseCommand.get_command,
                    filter(
                        lambda c_type: c_type
                        not in (
                            BotCommandType.INVALID,
                            BotCommandType.UNKNOWN,
                            BotCommandType.BASE,
                        ),
                        list(BotCommandType),
                    ),
                ),
            ),
            key=lambda c: str(c.command_type.value),
        ):
            bot_command = BotCommand(
                str(command.command_type.value), command.command_description
            )
            if command.required_role_level.value <= role.value:
                commands.append(bot_command)

        return list(commands)

    res = collections.deque()
    for user_vertex in admins_and_owners:
        if user_vertex.role in (UserRole.ADMIN, UserRole.OWNER):
            res.append(
                {
                    "scope": BotCommandScopeChat(user_vertex.user_id),
                    "commands": populate_commands(user_vertex.role),
                }
            )

    res.append(
        {
            "scope": BotCommandScopeDefault(),
            "commands": populate_commands(UserRole.SEARCHER),
        }
    )

    return list(res)
