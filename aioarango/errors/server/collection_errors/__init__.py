"""
Collection Exceptions
"""

from .collection_checksum_error import CollectionChecksumError
from .collection_configure_error import CollectionConfigureError
from .collection_create_error import CollectionCreateError
from .collection_delete_error import CollectionDeleteError
from .collection_list_error import CollectionListError
from .collection_load_error import CollectionLoadError
from .collection_properties_error import CollectionPropertiesError
from .collection_recalculate_error import CollectionRecalculateCountError
from .collection_rename_error import CollectionRenameError
from .collection_responsible_shard_error import CollectionResponsibleShardError
from .collection_revision_error import CollectionRevisionError
from .collection_statistics_error import CollectionStatisticsError
from .collection_truncate_error import CollectionTruncateError
from .collection_unload_error import CollectionUnloadError

__all__ = [
    "CollectionChecksumError",
    "CollectionConfigureError",
    "CollectionCreateError",
    "CollectionDeleteError",
    "CollectionListError",
    "CollectionLoadError",
    "CollectionPropertiesError",
    "CollectionRecalculateCountError",
    "CollectionRenameError",
    "CollectionResponsibleShardError",
    "CollectionRevisionError",
    "CollectionStatisticsError",
    "CollectionTruncateError",
    "CollectionUnloadError",
]
