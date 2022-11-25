from enum import Enum


class CollectionType(Enum):
    """
    Specifies the type of a collection.
    """

    UNKNOWN = 0
    DOCUMENT = 2
    EDGE = 3
