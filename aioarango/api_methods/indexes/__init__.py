from .create_full_text_index import CreateFullTextIndex
from .create_geo_index import CreateGeoIndex
from .read_all_collection_indexes import ReadAllCollectionIndexes


class IndexesMethods(
    CreateFullTextIndex,
    CreateGeoIndex,
    ReadAllCollectionIndexes,
):
    pass
