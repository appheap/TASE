from .create_collection import CreateCollection
from .drop_collection import DropCollection
from .read_all_collections import ReadAllCollections
from .read_collection_properties import ReadCollectionProperties
from .rename_collection import RenameCollection


class CollectionsMethods(
    CreateCollection,
    DropCollection,
    ReadAllCollections,
    ReadCollectionProperties,
    RenameCollection,
):
    pass
