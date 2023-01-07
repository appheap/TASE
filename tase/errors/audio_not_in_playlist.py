from .tase_error import TASEError


class AudioNotInPlaylist(TASEError):
    """`Audio` is not in the `Playlist`"""

    MESSAGE = "`Audio` with `key` `{}` is not in a `Playlist` with key `{}`"
