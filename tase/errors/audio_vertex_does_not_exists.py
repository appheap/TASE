from .tase_error import TASEError


class AudioVertexDoesNotExist(TASEError):
    """`Audio` vertex does not exist with the given `key`"""

    MESSAGE = "`Audio` vertex does not exist with `key` `{}`"
