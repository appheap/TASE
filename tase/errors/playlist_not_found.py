from .tase_error import TASEError


class PlaylistNotFound(TASEError):
    """`Playlist` vertex does not exist with the given key"""

    MESSAGE = "Playlist with key `{}` not found."
