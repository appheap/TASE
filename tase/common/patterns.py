import re
from typing import Optional, Deque

telegram_username_pattern = re.compile(
    r"(?:@|(?:(?:(?:https?://)?t(?:elegram)?)\.me\/))(?P<username>[a-zA-Z0-9_]{5,32})",
    re.IGNORECASE,
)


def remove_usernames(
    text: str,
    extra_strings_to_remove: Deque[str] = None,
) -> Optional[str]:
    """
    Remove usernames and `extra_string_to_remove` parameter from the given `text`

    Parameters
    ----------
    text : str
        Text string to remove the usernames from
    extra_strings_to_remove : deque, default : None
        Extra strings to remove from the `text` parameter

    Returns
    -------
    str, optional
        Modified text after removing usernames if successful, otherwise, return None

    """
    if text is None:
        return None

    text = telegram_username_pattern.sub("", text)
    if extra_strings_to_remove is not None and len(extra_strings_to_remove):
        for to_remove in extra_strings_to_remove:
            if to_remove is None:
                continue
            text = re.sub(to_remove, "", text, flags=re.IGNORECASE)

    return text
