from .tase_error import TASEError


class InvalidFromVertex(TASEError):
    """`from_vertex` class is invalid"""

    MESSAGE = "`from_vertex` class `{}` of `edge` `{}` is invalid"
