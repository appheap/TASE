from .create_collection import CreateCollection
from .drop_collection import DropCollection
from .read_all_collections import ReadAllCollections


class CollectionsMethods(
    CreateCollection,
    DropCollection,
    ReadAllCollections,
):
    pass
