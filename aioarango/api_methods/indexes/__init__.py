from .create_full_text_index import CreateFullTextIndex
from .create_geo_index import CreateGeoIndex
from .create_inverted_index import CreateInvertedIndex
from .create_multi_dimensional_index import CreateMultiDimensionalIndex
from .create_persistent_index import CreatePersistentIndex
from .create_ttl_index import CreateTTLIndex
from .delete_index import DeleteIndex
from .read_all_collection_indexes import ReadAllCollectionIndexes
from .read_index import ReadIndex


class IndexesMethods(
    CreateFullTextIndex,
    CreateGeoIndex,
    CreateInvertedIndex,
    CreateMultiDimensionalIndex,
    CreatePersistentIndex,
    CreateTTLIndex,
    DeleteIndex,
    ReadAllCollectionIndexes,
    ReadIndex,
):
    pass
