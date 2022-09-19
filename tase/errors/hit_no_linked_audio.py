from .tase_error import TASEError


class HitNoLinkedAudio(TASEError):
    """`Hit` vertex does not have any `Audio` vertex connected to it"""

    MESSAGE = (
        "`Hit` with `download_url` `{}` does not have any `Audio` vertex linked to it"
    )
