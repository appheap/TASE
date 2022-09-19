from .tase_error import TASEError


class ParamNotProvided(TASEError):
    """Parameter has not been passed to this method"""

    MESSAGE = "`{}` parameter has not been passed to this method"
