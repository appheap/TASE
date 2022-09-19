from .tase_error import TASEError


class PlaylistDoesNotExists(TASEError):
    """`Playlist` vertex does not exist with the given key"""

    MESSAGE = "User `{}` does not have a playlist with the key `{}`"
