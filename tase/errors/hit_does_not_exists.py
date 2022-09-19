from .tase_error import TASEError


class HitDoesNotExists(TASEError):
    """`Hit` vertex does not exists with the given `download_url`"""

    MESSAGE = "`Hit` vertex does not exist with `download_url` `{}`"
