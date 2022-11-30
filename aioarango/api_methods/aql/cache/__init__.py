from .change_aql_cache_properties import ChangeAQLCacheProperties
from .get_aql_cache_properties import GetAQLCacheProperties


class AQLCacheMethods(
    ChangeAQLCacheProperties,
    GetAQLCacheProperties,
):
    pass
