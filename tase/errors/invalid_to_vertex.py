from .tase_error import TASEError


class InvalidToVertex(TASEError):
    """`to_vertex` class is invalid"""

    MESSAGE = "`to_vertex` class `{}` of `edge` `{}` is invalid"
