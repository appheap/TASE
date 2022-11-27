from .create_full_text_index import CreateFullTextIndex
from .create_geo_index import CreateGeoIndex
from .create_inverted_index import CreateInvertedIndex
from .read_all_collection_indexes import ReadAllCollectionIndexes


class IndexesMethods(
    CreateFullTextIndex,
    CreateGeoIndex,
    CreateInvertedIndex,
    ReadAllCollectionIndexes,
):
    pass
