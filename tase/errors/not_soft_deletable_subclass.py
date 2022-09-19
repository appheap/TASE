from .tase_error import TASEError


class NotSoftDeletableSubclass(TASEError):
    """This class is not subclass of `BaseSoftDeletableDocument` class"""

    MESSAGE = "Class `{}` is not a subclass of `BaseSoftDeletableDocument` class"
