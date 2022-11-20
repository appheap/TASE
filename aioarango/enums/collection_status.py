from enum import Enum


class CollectionStatus(Enum):
    NEW = 1
    UNLOADED = 2
    LOADED = 3
    UNLOADING = 4
    DELETED = 5
    LOADING = 6
