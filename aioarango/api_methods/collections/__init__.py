from .change_collection_properties import ChangeCollectionProperties
from .compact_collection_data import CompactCollectionData
from .create_collection import CreateCollection
from .drop_collection import DropCollection
from .get_collection_checksum import GetCollectionChecksum
from .get_collection_document_count import GetCollectionDocumentCount
from .get_collection_statistics import GetCollectionStatistics
from .get_document_responsible_shard import GetDocumentResponsibleShard
from .load_indexes_into_memory import LoadIndexesIntoMemory
from .read_all_collections import ReadAllCollections
from .read_collection_info import ReadCollectionInfo
from .read_collection_properties import ReadCollectionProperties
from .recalculate_collection_document_count import RecalculateCollectionDocumentCount
from .rename_collection import RenameCollection
from .truncate_collection import TruncateCollection


class CollectionsMethods(
    ChangeCollectionProperties,
    CompactCollectionData,
    CreateCollection,
    DropCollection,
    GetCollectionChecksum,
    GetCollectionDocumentCount,
    GetCollectionStatistics,
    GetDocumentResponsibleShard,
    LoadIndexesIntoMemory,
    ReadAllCollections,
    ReadCollectionInfo,
    ReadCollectionProperties,
    RecalculateCollectionDocumentCount,
    RenameCollection,
    TruncateCollection,
):
    pass
