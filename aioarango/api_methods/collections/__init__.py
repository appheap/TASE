from .create_collection import CreateCollection
from .drop_collection import DropCollection
from .read_all_collections import ReadAllCollections
from .read_collection_info import ReadCollectionInfo
from .read_collection_properties import ReadCollectionProperties
from .rename_collection import RenameCollection
from .truncate_collection import TruncateCollection


class CollectionsMethods(
    CreateCollection,
    DropCollection,
    ReadAllCollections,
    ReadCollectionInfo,
    ReadCollectionProperties,
    RenameCollection,
    TruncateCollection,
):
    pass
