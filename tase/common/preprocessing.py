import mimetypes
import re
import string
import unicodedata
from typing import Set, Callable, Optional, List, Tuple

import emoji
import nltk

url_regex = r"(?i)(?:[a-zA-Z]+://)?(?:www[./])?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9@:%_\\+.~#?&\\/=]*)"
stop_words_regex = r"""(?x)                          # Set flag to allow verbose regexps
          \w+(?:-\w+)*                              # Words with optional internal hyphens 
          | \s*                                     # Any space
          | [][!"#$%&'*+,-./:;<=>?@\\^():_`{|}~]    # Any symbol 
        """

punctuation_chars = string.punctuation
punctuation_chars_without_dot = string.punctuation.replace(".", "")
tags_regex = r"@[a-zA-Z0-9_]+"
html_tags_regex = r"""(?x)                              # Turn on free-spacing
          <[^>]+>                                       # Remove <html> tags
          | &([a-z0-9]+|\#[0-9]{1,6}|\#x[0-9a-f]{1,6}); # Remove &nbsp;
          """
hashtags_regex = r"#\w+"
telegram_url_regex = r"(?:(?:https?://)?(?:www\.)?(?:t(?:elegram)?\.(?:org|me|dog)/(?:joinchat/|\+))([\w-]+)|(?:https?://)?(?:www\.)?(?:t(?:elegram)?\.(?:org|me|dog)/)(proxy\?.+)|(?:https?://)?(?:www\.)?(?:t(?:elegram)?\.(?:org|me|dog)/)(c/\d+/\d+/?)|(?:(?:(?:(?:https?://)?t(?:elegram)?)\.me\/)(?P<username1>[a-zA-Z0-9_]{5,32})|(?:@)(?P<username2>[a-zA-Z0-9_]{5,32})(?:$|\s)|((?:https?://)?(?P<username0>[a-zA-Z0-9_]{5,32})(\.t(elegram)?\.me)))(?:(/\d+/?)|.+)?)"

mimetypes = mimetypes.MimeTypes(("common/mime_types_file",))

try:
    # If not present, download NLTK stopwords.
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords")

from nltk.corpus import stopwords as nltk_en_stopwords
from spacy.lang.en import stop_words as spacy_en_stopwords

DEFAULT = set(nltk_en_stopwords.words("english"))
NLTK_EN = DEFAULT
SPACY_EN = spacy_en_stopwords.STOP_WORDS


def empty_to_null(text: str) -> Optional[str]:
    if text is None or not len(text):
        return None

    return text


def replace_telegram_urls(
    text: str,
    symbol: str,
) -> Optional[str]:
    if text is None or symbol is None:
        return None

    return re.sub(
        telegram_url_regex,
        symbol,
        text,
    )


def remove_telegram_urls(text: str) -> Optional[str]:
    if text is None:
        return None

    return replace_telegram_urls(text, "")


def lowercase(text: str) -> Optional[str]:
    if text is None:
        return None

    return text.lower()


def remove_html_tags(text: str) -> Optional[str]:
    if text is None:
        return None

    return re.sub(html_tags_regex, "", text)


def replace_digits(
    text: str,
    symbols: str = " ",
    only_blocks=True,
) -> Optional[str]:
    if text is None:
        return None

    if only_blocks:
        return re.sub(r"\b\d+\b", symbols, text)
    else:
        return re.sub(r"\d+", symbols, text)


def remove_digits(
    text: str,
    only_blocks=True,
) -> Optional[str]:
    if text is None:
        return None

    return replace_digits(text, "", only_blocks)


def replace_tags(
    text: str,
    symbol: str,
) -> Optional[str]:
    if text is None:
        return None

    return re.sub(tags_regex, symbol, text)


def remove_tags(text: str) -> Optional[str]:
    if text is None:
        return None

    return replace_tags(text, "")


def replace_hashtags(
    text: str,
    symbol: str,
) -> Optional[str]:
    if text is None:
        return None

    return re.sub(hashtags_regex, symbol, text)


def remove_hashtags(text: str) -> Optional[str]:
    if text is None:
        return None

    return replace_hashtags(text, "")


def replace_punctuation(
    text: str,
    symbol: str = " ",
) -> Optional[str]:
    if text is None:
        return None

    table = str.maketrans({key: symbol for key in string.punctuation})
    return text.translate(table)


def remove_punctuation(text: str) -> Optional[str]:
    if text is None:
        return None

    return text.translate(str.maketrans("", "", punctuation_chars))


def replace_punctuation_without_dot(
    text: str,
    symbol: str = " ",
) -> Optional[str]:
    if text is None:
        return None
    table = str.maketrans({key: symbol for key in punctuation_chars_without_dot})
    return text.translate(table)


def remove_punctuation_without_dot(text: str) -> Optional[str]:
    return text.translate(str.maketrans("", "", punctuation_chars_without_dot))


def remove_diacritics(text: str) -> Optional[str]:
    if text is None:
        return None

    nfkd_form = unicodedata.normalize("NFKD", text)
    # unicodedata.combining(char) checks if the character is in composed form (consisting of several unicode chars combined), i.e. a diacritic
    return "".join([char for char in nfkd_form if not unicodedata.combining(char)])


def remove_whitespace(text: str) -> Optional[str]:
    if text is None:
        return None

    return " ".join(text.replace("\xa0", " ").split())


def replace_stopwords(
    text: str,
    symbol: str,
    stopwords_: Optional[Set[str]] = None,
) -> Optional[str]:
    if text is None:
        return None

    if stopwords_ is None:
        import stopwords

        stopwords_ = stopwords.DEFAULT

    return "".join(t if t not in stopwords_ else symbol for t in re.findall(stop_words_regex, text))


def remove_stopwords(
    text: str,
    stopwords: Optional[Set[str]] = None,
) -> Optional[str]:
    if text is None:
        return None

    return replace_stopwords(text, symbol="", stopwords_=stopwords)


def replace_urls(
    text: str,
    symbol: str,
) -> Optional[str]:
    if text is None:
        return None

    return re.sub(url_regex, symbol, text)


def remove_urls(text: str) -> Optional[str]:
    if text is None:
        return None

    return replace_urls(text, " ")


def remove_lines(text: str) -> Optional[str]:
    if text is None:
        return None

    return text.replace("\n", " ")


def remove_extra_spaces(text: str) -> Optional[str]:
    if text is None:
        return None

    return re.sub(r"\s{2}", " ", text).strip()


def guess_mime_type(filename: str) -> Optional[str]:
    return mimetypes.guess_type(filename)[0]


def guess_extension(mime_type: str) -> Optional[str]:
    return mimetypes.guess_extension(mime_type)


def separate_file_name_and_extension(text: str) -> Tuple[Optional[str], Optional[str]]:
    if text is None:
        return None, None

    mime_type = guess_mime_type(text)
    if mime_type is None:
        return text, None

    if not mime_type.startswith("audio/"):
        return text, None

    ext = guess_extension(mime_type)
    if ext is None:
        return text, None

    file_name = text[: text.lower().find(ext)]
    extension = text[text.lower().find(ext) :]

    return file_name, extension


def remove_audio_file_extension(text: str) -> Optional[str]:
    """
    Guess the file name by filtering out extension part

    Parameters
    ----------
    text : str
        Raw file name string

    Returns
    -------
    str, optional
        File name without the extension part

    """
    if text is None:
        return None

    mime_type = guess_mime_type(text)
    if mime_type is None:
        return text

    if not mime_type.startswith("audio/"):
        return text

    ext = guess_extension(mime_type)
    if ext is None:
        return text

    temp = text[: text.lower().find(ext)]
    if not len(temp):
        return None
    return temp


def replace_emojis(
    text: str,
    symbol: str = " ",
) -> Optional[str]:
    if text is None:
        return None

    return emoji.replace_emoji(text, symbol)


def remove_emojis(text: str) -> Optional[str]:
    return replace_emojis(text, "")


###################################################################


def get_default_pipeline() -> List[Callable[[str], str]]:
    """
    Return a list containing all the methods used in the default cleaning pipeline.

    Return a list with the following functions:
     1. :meth:`tase.common.preprocessing.remove_diacritics`
     2. :meth:`tase.common.preprocessing.remove_file_extension`
     3. :meth:`tase.common.preprocessing.remove_html_tags`
     4. :meth:`tase.common.preprocessing.remove_telegram_urls`
     5. :meth:`tase.common.preprocessing.remove_urls`
     6. :meth:`tase.common.preprocessing.replace_punctuation`
     7. :meth:`tase.common.preprocessing.remove_emojis`
     8. :meth:`tase.common.preprocessing.remove_whitespace`
     9. :meth:`tase.common.preprocessing.remove_lines`
     10. :meth:`tase.common.preprocessing.remove_extra_spaces`
     11. :meth:`tase.common.preprocessing.empty_to_null`
    """
    return [
        # lowercase,
        remove_diacritics,  # this one needs to come first to prevent decoding error
        remove_audio_file_extension,
        remove_html_tags,
        remove_telegram_urls,
        remove_urls,
        replace_punctuation,
        remove_emojis,
        remove_whitespace,
        remove_lines,
        remove_extra_spaces,
        empty_to_null,
    ]


default_pipeline = get_default_pipeline()


def get_audio_item_pipeline() -> List[Callable[[str], str]]:
    """
    Return a list containing all the methods used in the cleaning pipeline for audio items returned to the user.

    Returns
    -------
    list of callables
        List of function objects used for cleaning

    """
    return [
        # remove_diacritics,  # this one needs to come first to prevent decoding error
        remove_html_tags,
        remove_telegram_urls,
        remove_urls,
        remove_hashtags,
        # remove_punctuation_without_dot,
        replace_punctuation_without_dot,
        remove_emojis,
        remove_whitespace,
        remove_lines,
        remove_extra_spaces,
    ]


audio_item_pipeline = get_audio_item_pipeline()


def clean_audio_item_text(
    text: str,
    remove_file_extension_: bool = False,
    is_file_name: bool = False,
) -> Optional[str]:
    extension = None
    if is_file_name:
        text, extension = separate_file_name_and_extension(text)

    text = clean_text(text, audio_item_pipeline)
    if remove_file_extension_:
        text = remove_audio_file_extension(text)

    if is_file_name:
        if text is not None and extension is not None and not remove_file_extension_:
            text = text + extension

    return text


def get_hashtag_cleaning_pipeline() -> List[Callable[[str], str]]:
    """
    Return a list containing all the methods used in the cleaning pipeline for hashtags.

    Returns
    -------
    list of callables
        List of function objects used for cleaning

    """
    return [
        remove_diacritics,
        lowercase,
        remove_emojis,
        remove_lines,
        remove_extra_spaces,
    ]


hashtag_cleaning_pipeline = get_hashtag_cleaning_pipeline()


def clean_hashtag(text: str) -> Optional[str]:
    return clean_text(text, hashtag_cleaning_pipeline)


def clean_text(
    text: str,
    pipeline: List[Callable] = None,
) -> Optional[str]:
    if text is None:
        return None

    from tase.my_logger import logger

    if pipeline is None or not len(pipeline):
        pipeline = default_pipeline

    for op in pipeline:
        try:
            text = op(text)
        except UnicodeDecodeError:
            logger.error(f"UnicodeDecodeError: {text}")

    return text


if __name__ == "__main__":
    print(remove_audio_file_extension("test.mp3"))  # must print `text`
