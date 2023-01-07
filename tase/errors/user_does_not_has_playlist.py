from .tase_error import TASEError


class UserDoesNotHasPlaylist(TASEError):
    """`Playlist` vertex does not exist with the given key"""

    MESSAGE = "User `{}` does not have a playlist with the key `{}`"
