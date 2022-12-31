from .tase_error import TASEError


class HitNoLinkedPlaylist(TASEError):
    """`Hit` vertex does not have any `Playlist` vertex connected to it"""

    MESSAGE = "`Hit` with `download_url` `{}` does not have any `Playlist` vertex linked to it"
