from .change_aql_cache_properties import ChangeAQLCacheProperties
from .clear_aql_cache_entries import ClearAQLCacheEntries
from .get_aql_cache_entries import GetAQLCacheEntries
from .get_aql_cache_properties import GetAQLCacheProperties


class AQLCacheMethods(
    ChangeAQLCacheProperties,
    ClearAQLCacheEntries,
    GetAQLCacheEntries,
    GetAQLCacheProperties,
):
    pass
