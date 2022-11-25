from .create_collection import CreateCollection
from .read_all_collections import ReadAllCollections


class CollectionsMethods(
    CreateCollection,
    ReadAllCollections,
):
    pass
