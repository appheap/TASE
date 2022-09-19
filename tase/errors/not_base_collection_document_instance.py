from .tase_error import TASEError


class NotBaseCollectionDocumentInstance(TASEError):
    """This class is not an instance of `BaseCollectionDocument` class"""

    MESSAGE = "Class `{}` is not an instance of `BaseCollectionDocument` class"
