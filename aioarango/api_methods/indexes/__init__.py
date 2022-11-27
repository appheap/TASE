from .create_full_text_index import CreateFullTextIndex
from .read_all_collection_indexes import ReadAllCollectionIndexes


class IndexesMethods(
    CreateFullTextIndex,
    ReadAllCollectionIndexes,
):
    pass
